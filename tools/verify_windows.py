"""Install the actual artifact and verify its bundled tools and desktop window."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def has_app_window():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    found = []

    @callback_type
    def inspect_window(handle, _):
        title = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(handle, title, len(title))
        if user32.IsWindowVisible(handle) and 'ParrMotion' in title.value:
            found.append(title.value)
        return True

    user32.EnumWindows(inspect_window, 0)
    return bool(found)


def main():
    if sys.platform != 'win32':
        raise SystemExit('Run the packaged desktop check on Windows.')
    root = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory(prefix='ParrMotion install check ') as directory:
        install = Path(directory) / 'Installed App'
        subprocess.run([str(root / 'dist' / 'ParrMotion-Setup-windows-x64.exe'),
                        '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART',
                        f'/DIR={install}', f'/LOG={Path(directory) / "setup.log"}'],
                       check=True, timeout=180)
        for name, argument in [('deno.exe', '--version'), ('ffmpeg.exe', '-version'),
                               ('ffprobe.exe', '-version')]:
            subprocess.run([str(install / name), argument], check=True,
                           stdout=subprocess.DEVNULL, timeout=30)
        environment = os.environ.copy()
        # Prevent Flet from silently installing missing packages during the check.
        environment['PIP_NO_INDEX'] = '1'
        process = subprocess.Popen([str(install / 'ParrMotion.exe')], cwd=directory,
                                   env=environment)
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f'Installed application exited early: {process.returncode}')
                if has_app_window():
                    print('Installed desktop window opened; bundled Deno and FFmpeg passed.')
                    break
                time.sleep(1)
            else:
                raise RuntimeError('Installed application did not open a ParrMotion window.')
        finally:
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            process.wait(timeout=30)
        subprocess.run([str(install / 'unins000.exe'), '/VERYSILENT',
                        '/SUPPRESSMSGBOXES', '/NORESTART'], check=True, timeout=120)
        if (install / 'ParrMotion.exe').exists():
            raise RuntimeError('Uninstall left the application executable behind.')
        print('Installer, desktop startup, runtime versions and uninstall checks passed.')


if __name__ == '__main__':
    main()
