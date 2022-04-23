from __future__ import annotations

from subprocess import check_output

from imageio_ffmpeg import get_ffmpeg_exe

__all__ = ('FFMpegWrapper',)


class FFMpegWrapper:
    __slots__ = ()
    DEFAULT_FFMPEG_LOG_LEVEL = 'panic'
    DEFAULT_ARGS = ()
    FFMPEG_EXE = get_ffmpeg_exe()

    @classmethod
    def convert(cls, *args, loglevel=None):
        if not loglevel:
            loglevel = cls.DEFAULT_FFMPEG_LOG_LEVEL
        check_output([cls.FFMPEG_EXE, '-v', loglevel, *cls.DEFAULT_ARGS, *args])

    @staticmethod
    def replace_audio_in_video(video_path: str, audio_path: str, output_path: str):
        FFMpegWrapper.convert('-i', video_path, '-i', audio_path,
                              '-map', '0:0', '-map', '1:0', '-c', 'copy',
                              output_path)
