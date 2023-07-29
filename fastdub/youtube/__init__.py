from fastdub.youtube import yt_upload

__all__ = ('SUPPORTED',)
try:
    from pafy.backend_youtube_dl import YtdlPafy

    from fastdub.youtube import downloader
    from fastdub.youtube import subtitles
except ImportError as e:
    from typing import Any as YtdlPafy

    SUPPORTED = False
else:
    SUPPORTED = True
    __all__ += ('downloader', 'subtitles', 'YtdlPafy')
