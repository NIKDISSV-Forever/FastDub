from __future__ import annotations

import os.path
import re
import sys
from pathlib import Path
from subprocess import check_call, getoutput

from imageio_ffmpeg import get_ffmpeg_exe

from fastdub import GlobalSettings

__all__ = ('FFMpegWrapper', 'DefaultFFMpegParams')


class DefaultFFMpegParams:
    __slots__ = ()
    ffmpeg_log_level = 'panic'
    args = ()
    executable = get_ffmpeg_exe()


def _ignore():
    pass


def _get_default_font_args() -> str:
    dirs = []
    if sys.platform == 'win32':
        if windir := os.environ.get('WINDIR'):
            dirs.append(str(Path(windir, 'fonts')))
    elif sys.platform in {'linux', 'linux2'}:
        dirs += [os.path.join(lindir, "fonts") for lindir in
                 (os.environ.get('XDG_DATA_DIRS') or '/usr/share').split(":")]
    elif sys.platform == 'darwin':
        dirs += [
            '/Library/Fonts',
            '/System/Library/Fonts',
            os.path.expanduser('~/Library/Fonts'),
        ]

    for directory in dirs:
        for walkroot, walkdir, walkfilenames in os.walk(directory, onerror=_ignore):
            for walkfilename in walkfilenames:
                walkfilename = Path(walkfilename)
                if walkfilename.suffix == '.ttf':
                    return f":fontfile='{Path(walkroot, walkfilename)}'"
    return ''


class FFMpegWrapper:
    __slots__ = ()
    DURATION_RE = re.compile(r'Duration: (\d\d):(\d\d):(\d\d\.\d\d)')

    @classmethod
    def convert(cls, *args, loglevel=None):
        if not loglevel:
            loglevel = DefaultFFMpegParams.ffmpeg_log_level
        check_call([str(i) for i in (DefaultFFMpegParams.executable, '-v', loglevel, *DefaultFFMpegParams.args, *args)])

    @classmethod
    def get_video_duration_ms(cls, video_path: str | Path) -> float:
        return cls.get_video_duration_s(video_path) * 1000.

    @classmethod
    def get_video_duration_s(cls, video_path: str | Path) -> float:
        found = cls.DURATION_RE.search(getoutput(f'{DefaultFFMpegParams.executable} -i {video_path}'))
        if not found:
            return 0.
        groups = found.groups()
        return float(groups[0]) * 3600. + float(groups[1]) * 60. + float(groups[2])

    @classmethod
    def save_result_data(cls, video_path, audio_path, subtitles_path, output_path):
        inputs = '-i', video_path, '-i', audio_path, '-i', subtitles_path
        maps = '-map', '0:0', '-map', '1:0', '-map', '0:1', '-map', '2:0'
        copy_codec = '-c'
        watermark_args = ()

        subtitles_path = Path(subtitles_path)
        if (subtitles_path := subtitles_path.with_stem(f'_{subtitles_path.stem}')).is_file():
            inputs += '-i', subtitles_path
            maps += '-map', '3:0'
        if GlobalSettings.watermark:
            watermark_args = cls.get_watermark_vf(GlobalSettings.watermark)
            copy_codec = '-c:a'

        FFMpegWrapper.convert(
            *inputs, *maps,
            '-disposition:a:0', 'default', '-disposition:a:1', '0',
            *watermark_args, copy_codec, 'copy', '-c:s', 'mov_text',
            output_path)

    @classmethod
    def get_watermark_vf(cls, text: str) -> tuple[str, str]:
        return ('-vf',
                f"drawtext=text='{text}'{_get_default_font_args()}"
                ":fontcolor=white@0.5:box=1:boxcolor=black@0.5"
                ":x='mod(n,w-text_w)':y='mod(n,h-text_h)'")
