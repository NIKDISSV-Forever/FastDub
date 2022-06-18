from __future__ import annotations

import multiprocessing.pool
from pathlib import Path
from shutil import get_terminal_size
from typing import Callable, Iterable, Optional, TypeVar
from urllib.parse import urlparse

from FastDub.YT import *

__all__ = 'DownloadYTVideo',
_API_RET_TYPE = TypeVar('_API_RET_TYPE')


class DownloadYTVideo:
    __slots__ = ('save_dir', 'language', 'playlist', 'API_KEYS')

    def __init__(self, url: str, language: str, api_keys: Iterable[str] = ()):
        self.API_KEYS = {pafy_g.api_key, 'AIzaSyCHxJ84-ryessLJfWZVWldiuVCnxtf0Nm4', *api_keys}

        url_path = urlparse(url).path
        if url_path == '/playlist':
            playlist = self.with_api_key(lambda: pafy.get_playlist2(url))
            save_dir = playlist.plid
        elif (path_split := url_path.strip('/').split('/')) and path_split[0] in ('c', 'channel'):
            playlist = self.with_api_key(lambda: pafy.get_channel((path_split[1:] or (url,))[0]).uploads)
            save_dir = playlist.plid
        else:
            playlist = self.with_api_key(lambda: (pafy.new(url),))
            save_dir = playlist[0].videoid
        save_dir = Path(save_dir)
        if not save_dir.is_dir():
            save_dir.mkdir()

        self.save_dir = save_dir
        self.language = language
        self.playlist = playlist

    def multiprocessing_download(self, pc: int = None):
        if pc is None:
            pc = multiprocessing.cpu_count()
        if pc < 2:
            for yt_dl in self.playlist:
                self.download(yt_dl)
            return
        with multiprocessing.pool.ThreadPool(pc) as pool:
            pool.map(self.download, self.playlist)

    def download(self, yt_dl: YtdlPafy):
        save_to = self.save_dir / yt_dl.videoid
        srt_file = Path(f'{save_to}.srt')
        if not srt_file.is_file():
            Subtitles.download_srt(yt_dl.videoid, self.language, srt_file)
        mp4_file = Path(f'{save_to}.mp4')
        if not mp4_file.is_file():
            try:
                self.with_api_key(self.mp4_downloader(yt_dl, mp4_file))
                print(f'\r{mp4_file} downloaded.'.ljust(get_terminal_size().columns))
            except OSError:
                pass

    def with_api_key(self, func: Callable[[], _API_RET_TYPE]) -> Optional[_API_RET_TYPE]:
        for key in self.API_KEYS:
            pafy.set_api_key(key)
            try:
                return func()
            except pafy.util.GdataError:
                continue

    def mp4_downloader(self, yt_dl: YtdlPafy, mp4_file: str | Path):
        return lambda: yt_dl.getbest('mp4').download(f'{mp4_file}',
                                                     progress='MB',
                                                     callback=self.progress_callback)

    @staticmethod
    def progress_callback(total: int, downloaded: float, ratio: float, rate: float, eta: float):
        print(
            end=f'\r[{ratio:.2%}] {downloaded:,.2f}/{total / 1048576:,.2f}MB. {rate:,.2f} kb/s: '
                f'ETA {eta} sec.'.ljust(get_terminal_size().columns),
            flush=True)
