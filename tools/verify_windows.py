"""Verify installed resources and rendered UI, including a negative control."""
import ctypes
from ctypes import wintypes
import hashlib
from importlib.resources import files
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile


ICON_RESOURCES = ('controls/material/icons.json', 'controls/cupertino/cupertino_icons.json')
REQUIRED_TEXT = ('start download', 'save location', 'quality', 'paste video link')
ERROR_TEXT = ('encountered an error', 'no such file', 'traceback', 'unhandled exception')


def app_windows(process_ids):
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    found = []

    @callback_type
    def inspect_window(handle, _):
        title = ctypes.create_unicode_buffer(512)
        process_id = wintypes.DWORD()
        user32.GetWindowTextW(handle, title, len(title))
        user32.GetWindowThreadProcessId(handle, ctypes.byref(process_id))
        if process_id.value in process_ids and user32.IsWindowVisible(handle):
            bounds = wintypes.RECT()
            user32.GetWindowRect(handle, ctypes.byref(bounds))
            area = (bounds.right - bounds.left) * (bounds.bottom - bounds.top)
            if area > 100_000:
                found.append((area, handle))
        return True

    user32.EnumWindows(inspect_window, 0)
    return [handle for _, handle in sorted(found)]


def check_assets(install, portable):
    with zipfile.ZipFile(portable) as archive:
        for relative in ICON_RESOURCES:
            source = files('flet').joinpath(relative).read_bytes()
            path = install / '_internal' / 'flet' / relative
            installed = path.read_bytes()
            packed = archive.read('_internal/flet/' + relative)
            if source != installed or source != packed:
                raise RuntimeError(f'Flet resource differs between source, ZIP and installation: {relative}')
            if not json.loads(installed):
                raise RuntimeError(f'Empty Flet icon resource: {relative}')
            print(f'Installed and portable resource verified: {relative}; sha256={hashlib.sha256(installed).hexdigest()}')


def check_desktop(install, directory, evidence, tesseract, expect_error=False):
    from PIL import ImageGrab
    import psutil

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    label = 'missing-icons-negative-control' if expect_error else 'installed-desktop'
    screenshot = evidence / f'{label}.png'
    environment = os.environ.copy()
    environment['PIP_NO_INDEX'] = '1'
    environment['OMP_THREAD_LIMIT'] = '1'
    environment['LOCALAPPDATA'] = str(Path(directory) / label)
    process = subprocess.Popen([str(install / 'ParrMotion.exe')], cwd=directory, env=environment)
    consecutive = 0
    try:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f'Installed application exited early: {process.returncode}')
            children = psutil.Process(process.pid).children(recursive=True)
            windows = app_windows({process.pid, *(child.pid for child in children)})
            if not windows:
                time.sleep(1)
                continue
            handle = windows[-1]
            user32.ShowWindow(handle, 9)
            user32.SetForegroundWindow(handle)
            time.sleep(1)
            ImageGrab.grab(window=handle).save(screenshot)
            result = subprocess.run([tesseract, str(screenshot), 'stdout', '-l', 'eng', '--psm', '11'],
                                    capture_output=True, text=True, encoding='utf-8',
                                    env=environment, check=True, timeout=30)
            (evidence / f'{label}-ocr.txt').write_text(result.stdout, encoding='utf-8')
            text = re.sub(r'\s+', ' ', result.stdout).casefold()
            errors = [phrase for phrase in ERROR_TEXT if phrase in text]
            if errors:
                if expect_error:
                    print('Negative control: missing icons.json produced an error page and was correctly rejected.')
                    return
                raise RuntimeError(f'Rendered application error page: {text}')
            if all(phrase in text for phrase in REQUIRED_TEXT):
                if expect_error:
                    raise RuntimeError('Negative control unexpectedly rendered the main page without icons.json.')
                consecutive += 1
                if consecutive >= 2:
                    print('Rendered main page verified in two screenshots: ' + ', '.join(REQUIRED_TEXT))
                    print('MAIN_PAGE_OCR: ' + text)
                    return
            else:
                consecutive = 0
        raise RuntimeError(f'Expected rendered UI did not appear; see {screenshot} and OCR evidence.')
    finally:
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.wait(timeout=30)


def main():
    if sys.platform != 'win32':
        raise SystemExit('Run the packaged desktop check on Windows.')
    ctypes.windll.user32.SetProcessDPIAware()
    if ctypes.windll.kernel32.GetUserDefaultUILanguage() != 1033:
        raise SystemExit('Screenshot OCR verification requires an en-US Windows runner.')
    root = Path(__file__).resolve().parent.parent
    evidence = root / 'dist' / 'verification'
    evidence.mkdir(parents=True, exist_ok=True)
    tesseract = shutil.which('tesseract')
    if not tesseract:
        tesseract = str(Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Tesseract-OCR' / 'tesseract.exe')
    if not Path(tesseract).is_file():
        raise SystemExit('Tesseract OCR is required to verify the rendered desktop page.')
    with tempfile.TemporaryDirectory(prefix='ParrMotion install check ') as directory:
        install = Path(directory) / 'Installed App'
        subprocess.run([str(root / 'dist' / 'ParrMotion-Setup-windows-x64.exe'),
                        '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART',
                        f'/DIR={install}', f'/LOG={evidence / "setup.log"}'],
                       check=True, timeout=180)
        check_assets(install, root / 'dist' / 'ParrMotion-windows-x64.zip')
        for name, argument in [('deno.exe', '--version'), ('ffmpeg.exe', '-version'),
                               ('ffprobe.exe', '-version')]:
            subprocess.run([str(install / name), argument], check=True,
                           stdout=subprocess.DEVNULL, timeout=30)
        icons = install / '_internal' / 'flet' / ICON_RESOURCES[0]
        hidden = icons.with_suffix('.json.hidden')
        icons.rename(hidden)
        try:
            check_desktop(install, directory, evidence, tesseract, expect_error=True)
        finally:
            hidden.rename(icons)
        check_desktop(install, directory, evidence, tesseract)
        subprocess.run([str(install / 'unins000.exe'), '/VERYSILENT',
                        '/SUPPRESSMSGBOXES', '/NORESTART'], check=True, timeout=120)
        if (install / 'ParrMotion.exe').exists():
            raise RuntimeError('Uninstall left the application executable behind.')
        (evidence / 'result.json').write_text(json.dumps({
            'result': 'passed', 'negative_control_rejected': True,
            'main_page_text': REQUIRED_TEXT, 'flet_resources': ICON_RESOURCES,
            'runtime_versions': 'passed', 'uninstall': 'passed',
        }, indent=2), encoding='utf-8')
        print('Installer resources, rendered main page, negative control, runtimes and uninstall checks passed.')


if __name__ == '__main__':
    main()
