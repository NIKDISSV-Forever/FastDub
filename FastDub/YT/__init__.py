try:
    import download_youtube_subtitle.main
    from FastDub.YT import Subtitles
    from FastDub.YT import pafy
    from FastDub.YT.pafy import g
    from FastDub.YT.pafy.backend_youtube_dl import YtdlPafy
except ImportError as e:
    from typing import Any as YtdlPafy
    SUPPORTED = False
else:
    SUPPORTED = True
