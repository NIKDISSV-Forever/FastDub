from fastdub.youtube import yt_upload

try:
    from fastdub.youtube import downloader
    from fastdub.youtube import subtitles
    from fastdub.youtube.pafy.backend_youtube_dl import YtdlPafy
except ImportError as e:
    from typing import Any as YtdlPafy

    SUPPORTED = False
else:
    SUPPORTED = True
