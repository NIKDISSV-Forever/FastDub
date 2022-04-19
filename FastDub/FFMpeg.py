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
