import multiprocessing.pool
import os.path
import shutil
import urllib.parse
from typing import Callable, TypeVar, Optional, Iterable

from FastDub.YT import *

__all__ = 'DownloadYTVideo',
_API_RET_TYPE = TypeVar('_API_RET_TYPE')


class DownloadYTVideo:
    __slots__ = ('save_dir', 'language', 'playlist', 'API_KEYS')

    def __init__(self, url: str, language: str, api_keys: Iterable[str] = ()):
        self.API_KEYS = {g.api_key, 'AIzaSyCHxJ84-ryessLJfWZVWldiuVCnxtf0Nm4', *api_keys}

        if urllib.parse.urlparse(url).path == '/playlist':
            playlist = self.with_api_key(lambda: pafy.get_playlist2(url))
            save_dir = playlist.plid
        else:
            playlist = self.with_api_key(lambda: (pafy.new(url),))
            save_dir = playlist[0].videoid
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)

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
        save_to = os.path.join(self.save_dir, yt_dl.videoid)
        srt_file = f'{save_to}.srt'
        if not os.path.isfile(srt_file):
            Subtitles.download_srt(yt_dl.videoid, self.language, srt_file)
        mp4_file = f'{save_to}.mp4'
        if not os.path.isfile(mp4_file):
            try:
                self.with_api_key(self.mp4_downloader(yt_dl, mp4_file))
                print(f'\r{mp4_file} downloaded.'.ljust(shutil.get_terminal_size().columns))
            except OSError:
                pass

    def with_api_key(self, func: Callable[[], _API_RET_TYPE]) -> Optional[_API_RET_TYPE]:
        for key in self.API_KEYS:
            pafy.set_api_key(key)
            try:
                return func()
            except pafy.util.GdataError:
                continue

    def mp4_downloader(self, yt_dl: YtdlPafy, mp4_file: str):
        return lambda: yt_dl.getbest('mp4').download(mp4_file,
                                                     progress='MB',
                                                     callback=self.progress_callback)

    @staticmethod
    def progress_callback(total: int, downloaded: float, ratio: float, rate: float, eta: float):
        print(
            end=f'\r[{round(ratio * 100., 2)}%] {round(downloaded):,}/{total:,}MB. {round(rate, 1):,} kb/s: ETA'
                f' {eta} '
                f'sec.'.ljust(shutil.get_terminal_size().columns),
            flush=True)
