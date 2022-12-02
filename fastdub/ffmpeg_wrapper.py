from __future__ import annotations

from subprocess import check_call

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
        check_call((cls.FFMPEG_EXE, '-v', loglevel, *cls.DEFAULT_ARGS, *args))

    @staticmethod
    def save_result_data(video_path, audio_path, subtitles_path, output_path):
        FFMpegWrapper.convert('-i', video_path, '-i', audio_path, '-i', subtitles_path,
                              '-map', '0:0', '-map', '1:0', '-map', '0:1', '-map', '2:0',
                              '-disposition:a:0', 'default', '-disposition:a:1', '0',
                              '-c', 'copy', '-c:s', 'mov_text',
                              output_path)
