"""Build a Windows portable archive and installer from the repository root."""
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import sys


def main():
    if sys.platform != 'win32':
        raise SystemExit('Windows builds must run on Windows (or the Windows GitHub Actions workflow).')
    root = Path(__file__).resolve().parent.parent
    os.chdir(root)
    compiler = shutil.which('ISCC.exe')
    if not compiler:
        for variable in ('ProgramFiles(x86)', 'ProgramFiles'):
            candidate = Path(os.environ.get(variable, 'C:/Program Files (x86)')) / 'Inno Setup 6' / 'ISCC.exe'
            if candidate.is_file():
                compiler = str(candidate)
                break
    if not compiler:
        raise SystemExit('Missing Inno Setup 6: install it before building the Windows installer.')
    import deno
    tools = {'deno.exe': Path(deno.find_deno_bin())}
    for name in ('ffmpeg.exe', 'ffprobe.exe'):
        found = root / name
        if not found.is_file():
            # Chocolatey's PATH entry may be a shim tied to the build machine.
            # Copy the real package binary so the installer works elsewhere.
            package = Path(os.environ.get('ChocolateyInstall', 'C:/ProgramData/chocolatey')) / 'lib' / 'ffmpeg' / 'tools'
            packaged = sorted(package.rglob(name)) if package.is_dir() else []
            located = str(packaged[0]) if packaged else shutil.which(name)
            if not located:
                raise SystemExit(f'Missing {name}: put it beside main.py or add FFmpeg to PATH.')
            found = Path(located)
        tools[name] = found
        print(f'Bundling {name}: {found}', flush=True)
    subprocess.run([
        sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
        '--onedir', '--windowed', '--name', 'ParrMotion', '--icon', 'logo.ico',
        '--collect-all', 'flet_desktop', '--collect-all', 'yt_dlp',
        '--collect-all', 'yt_dlp_ejs', '--copy-metadata', 'yt-dlp',
        '--copy-metadata', 'yt-dlp-ejs', 'main.py',
    ], check=True)
    output = root / 'dist' / 'ParrMotion'
    for name, source in tools.items():
        shutil.copy2(source, output / name)
    shutil.copy2(root / 'LICENSE', output / 'LICENSE.txt')
    shutil.copy2(root / 'README.md', output / 'README.md')
    versions = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    (output / 'build-versions.txt').write_bytes(versions)
    (root / 'dist' / 'build-versions.txt').write_bytes(versions)
    shutil.make_archive(str(root / 'dist' / 'ParrMotion-windows-x64'), 'zip', output)
    subprocess.run([compiler, str(root / 'tools' / 'windows-installer.iss')], check=True)
    artifacts = [root / 'dist' / name for name in (
        'ParrMotion-windows-x64.zip', 'ParrMotion-Setup-windows-x64.exe')]
    checksums = ''
    for path in artifacts:
        with path.open('rb') as stream:
            checksums += f'{hashlib.file_digest(stream, "sha256").hexdigest()}  {path.name}\n'
    (root / 'dist' / 'SHA256SUMS.txt').write_text(checksums, encoding='utf-8')
    print('Built Windows installer and portable archive in dist/.')


if __name__ == '__main__':
    main()
