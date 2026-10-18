import asyncio
from contextlib import contextmanager
import functools
import http.server
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

import main as app
from download_support import DownloadLog, redact, runtime_options


class Page:
    def update(self):
        pass

    def add(self, *controls):
        self.controls = controls


@contextmanager
def application():
    """Capture real UI callbacks without launching a desktop process."""
    state = {}
    def capture(frame, event, arg):
        if event == 'return' and frame.f_code is app.main.__code__:
            state.update(frame.f_locals)
    with tempfile.TemporaryDirectory() as directory:
        with patch.dict(os.environ, {'LOCALAPPDATA': directory}):
            old_profile = sys.getprofile()
            try:
                sys.setprofile(capture)
                page = Page()
                app.main(page)
            finally:
                sys.setprofile(old_profile)
            try:
                yield state
            finally:
                for handler in state['download_log'].logger.handlers[:]:
                    handler.close()
                    state['download_log'].logger.removeHandler(handler)


class RuntimeTests(unittest.TestCase):
    def test_portable_tools_take_priority(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('deno', 'ffmpeg'):
                (root / (name + ('.exe' if os.name == 'nt' else ''))).touch()
            with patch('download_support.app_directory', return_value=root):
                options = runtime_options()
            self.assertEqual(options['ffmpeg_location'], str(root))
            self.assertEqual(list(options['js_runtimes']), ['deno'])
            self.assertTrue(options['js_runtimes']['deno']['path'].startswith(directory))

    def test_log_redacts_urls_and_headers(self):
        value = redact('https://user:password@example.com/video?token=secret\nCookie: private\nAuthorization: Bearer hidden')
        for private in ('password', 'secret', 'private', 'hidden', 'user:'):
            self.assertNotIn(private, value)
        self.assertIn('example.com/video', value)

    def test_log_persists_engine_version_and_full_error(self):
        with application() as state:
            log = state['download_log']
            message = 'HTTP Error 403: ' + 'full error details ' * 20
            log.error(message)
            contents = log.path.read_text(encoding='utf-8')
            self.assertIn(message, contents)
            self.assertIn('Engine yt-dlp', contents)


class ErrorTests(unittest.TestCase):
    def test_full_error_remains_visible(self):
        with application() as state:
            message = 'HTTP Error 403: ' + 'details ' * 30
            state['mailbox'].put({'type': 'error', 'content': message})
            asyncio.run(state['ui_updater']())
            self.assertIn(message, state['status_text'].value)
            self.assertIn(str(state['download_log'].path), state['status_text'].value)
            self.assertNotEqual(state['status_text'].opacity, 0)
            self.assertTrue(state['status_text'].selectable)

    def test_value_error_is_not_misreported_as_user_cancellation(self):
        with application() as state, tempfile.TemporaryDirectory() as directory:
            with patch.object(app.yt_dlp, 'YoutubeDL') as engine:
                engine.return_value.__enter__.return_value.extract_info.side_effect = ValueError('bad metadata')
                state['backend_worker']('https://example.com/video', directory, 'auto', '0')
                options = engine.call_args.args[0]
                self.assertIs(options['logger'], state['download_log'])
                self.assertTrue(options['noplaylist'])
            result = state['mailbox'].get_nowait()
            self.assertEqual(result, {'type': 'error', 'content': 'bad metadata'})


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
class LocalDownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        root = Path(cls.directory.name)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                        '-f', 'lavfi', '-i', 'testsrc=size=160x120:rate=10',
                        '-f', 'lavfi', '-i', 'sine=frequency=440', '-t', '1',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                        str(root / 'sample.mp4')], check=True)
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0),
            functools.partial(QuietHandler, directory=str(root)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/sample.mp4'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.directory.cleanup()

    def download(self, quality, extension):
        with application() as state, tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'new-output'
            state['backend_worker'](self.url, str(output), quality, '0')
            messages = []
            while not state['mailbox'].empty():
                messages.append(state['mailbox'].get_nowait())
            self.assertEqual(messages[-1]['type'], 'success', messages)
            files = list(output.glob('*.' + extension))
            self.assertEqual(len(files), 1)
            result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                     'format=duration', '-of', 'csv=p=0', str(files[0])],
                                    capture_output=True, text=True, check=True)
            self.assertGreater(float(result.stdout.strip()), 0)

    def test_video_download(self):
        self.download('auto', 'mp4')

    def test_mp3_conversion(self):
        self.download('audio', 'mp3')

    def test_explicit_cancellation(self):
        with application() as state, tempfile.TemporaryDirectory() as directory:
            state['cancel_flag'][0] = True
            state['backend_worker'](self.url, directory, 'auto', '0')
            messages = []
            while not state['mailbox'].empty():
                messages.append(state['mailbox'].get_nowait())
            self.assertEqual(messages[-1]['type'], 'cancelled', messages)
            self.assertFalse(list(Path(directory).glob('*.part')))


if __name__ == '__main__':
    unittest.main()
