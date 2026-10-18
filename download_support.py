"""Runtime discovery and persistent, redacted download diagnostics."""
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import re
import shutil
import sys
import sysconfig
import tempfile
from urllib.parse import urlsplit, urlunsplit

import yt_dlp.version


class DownloadCancelled(Exception):
    """A download was explicitly stopped by its user."""


def app_directory():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def runtime_options():
    options = {}
    root = app_directory()
    if (root / 'ffmpeg.exe').is_file() or (root / 'ffmpeg').is_file():
        options['ffmpeg_location'] = str(root)
    # The portable Windows build includes Deno next to the executable.
    for name in ('deno', 'node'):
        binary = root / (name + ('.exe' if os.name == 'nt' else ''))
        scripts_binary = Path(sysconfig.get_path('scripts')) / binary.name
        path = (str(binary) if binary.is_file() else
                str(scripts_binary) if scripts_binary.is_file() else shutil.which(name))
        if path:
            options['js_runtimes'] = {name: {'path': path}}
            break
    return options


def redact(message):
    def clean_url(match):
        value = match.group(0)
        try:
            parts = urlsplit(value)
            host = parts.hostname or ''
            if parts.port:
                host += ':' + str(parts.port)
            return urlunsplit((parts.scheme, host, parts.path,
                               '[redacted]' if parts.query else '', ''))
        except ValueError:
            return '[redacted URL]'
    text = re.sub(r'https?://[^\s<>\"\']+', clean_url, str(message))
    return re.sub(r'(?im)\b(cookie|authorization|proxy-authorization)\s*[:=].*',
                  r'\1: [redacted]', text)


class DownloadLog:
    def __init__(self):
        base = Path(os.environ.get('LOCALAPPDATA') or Path.home() / '.local' / 'state')
        self.path = base / 'ParrMotion' / 'logs' / 'download.log'
        logger = logging.getLogger('parrmotion.download')
        logger.setLevel(logging.INFO)
        logger.propagate = False
        if not logger.handlers:
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                handler = RotatingFileHandler(self.path, maxBytes=2_000_000,
                                              backupCount=2, encoding='utf-8')
            except OSError:
                self.path = Path(tempfile.gettempdir()) / 'ParrMotion' / 'download.log'
                self.path.parent.mkdir(parents=True, exist_ok=True)
                handler = RotatingFileHandler(self.path, maxBytes=2_000_000,
                                              backupCount=2, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            logger.addHandler(handler)
        self.path = Path(logger.handlers[0].baseFilename)
        self.logger = logger
        self.logger.info('Engine yt-dlp %s', yt_dlp.version.__version__)

    def debug(self, message):
        # yt-dlp sends normal informational messages through debug as well.
        # Exclude verbose internals, which may contain request headers.
        if not str(message).startswith('[debug] '):
            self.logger.info('%s', redact(message))

    def warning(self, message):
        self.logger.warning('%s', redact(message))

    def error(self, message):
        self.logger.error('%s', redact(message))
