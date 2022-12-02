from __future__ import annotations

import multiprocessing.pool
import re
from pathlib import Path
from typing import Callable, Optional, TypeVar
from urllib.parse import urlparse

import rich.live
import rich.table
from tqdm import tqdm
from youtubesearchpython import VideosSearch

from fastdub import PrettyViewPrefix
from fastdub.youtube import *
from fastdub.youtube import pafy
from fastdub.youtube.pafy import g as pafy_g
from fastdub.youtube.subtitles import download_srt

__all__ = ('DownloadYTVideo', 'with_api_key')

_API_RET_TYPE = TypeVar('_API_RET_TYPE')
_PATH_SUPPORTED = re.compile(r'[\\/:?"<>|]+')


def _path_save(name: str) -> str:
    return _PATH_SUPPORTED.sub('_', name)


class DownloadYTVideo:
    __slots__ = ('save_dir', 'language', 'playlist', 'api_keys',
                 'download_title',
                 '_table_data', '_live_progress')
    API_KEYS = {pafy_g.api_key, 'AIzaSyCHxJ84-ryessLJfWZVWldiuVCnxtf0Nm4'}
    TABLE_TITLE_TEMPLATE = 'Downloading from [link=%(scheme)s://%(netloc)s]%(netloc)s[/]...'

    def __init__(self, query: str,
                 language: str,
                 search_limit: int = 20,
                 region: str = 'US'):
        url_parsed = urlparse(query)
        url_path = url_parsed.path
        is_youtube = False
        if query.startswith('?'):
            query = query.removeprefix('?')
            is_youtube = True
            videos = tqdm(VideosSearch(query, search_limit, language, region).result().get('result', ()),
                          'Video search processing', unit='video', dynamic_ncols=True, colour='white')
            playlist = (
                *(with_api_key(lambda: pafy.new(data['id']))
                  for data in videos if data.get('type', '') == 'video'),)
            save_dir = query
        elif url_path == '/playlist':
            playlist = with_api_key(lambda: pafy.get_playlist2(query))
            save_dir = f'{playlist.title} [{playlist.plid}]'
        elif (path_split := url_path.strip('/').split('/')) and path_split[0] in ('c', 'channel'):
            playlist = with_api_key(lambda: pafy.get_channel((path_split[1:] or (query,))[0]).uploads)
            save_dir = f'{playlist.title} [{playlist.plid}]'
        else:
            playlist = with_api_key(lambda: (pafy.new(query),))
            playlist_0 = playlist[0]
            save_dir = f'{playlist_0.title} [{playlist_0.videoid}]'
        save_dir = Path(_path_save(' '.join(save_dir.split(' ')[:-1]) if len(save_dir) > 100 else save_dir))
        save_dir.mkdir(parents=True, exist_ok=True)

        self.save_dir = save_dir
        self.language = language
        self.playlist = playlist
        self.download_title = self.TABLE_TITLE_TEMPLATE % (
            {'scheme': 'https', 'netloc': 'www.youtube.com'} if is_youtube
            else {'scheme': url_parsed.scheme, 'netloc': url_parsed.netloc}
        )

    def download(self, yt_dl: YtdlPafy):
        title: str = yt_dl.title.strip()
        if len(title) <= (97 - len(yt_dl.videoid)):
            title += f' [{yt_dl.videoid}]'
        save_to = self.save_dir / title

        _file = Path(save_to)
        srt_file = _file.with_suffix('.srt')
        if not srt_file.is_file():
            download_srt(yt_dl.videoid, self.language, srt_file)
        mp4_file = _file.with_suffix('.mp4')
        if not mp4_file.is_file():
            try:
                with_api_key(self.mp4_downloader(yt_dl, mp4_file))
            except OSError:
                pass

    def mp4_downloader(self, yt_dl: YtdlPafy, mp4_file: str | Path):
        mp4_file = str(mp4_file)
        return lambda: yt_dl.getbest('mp4').download(mp4_file,
                                                     quiet=True,
                                                     callback=lambda *args: self.progress_callback(mp4_file, *args))

    def multiprocessing_download(self, pc: int = None):
        self._table_data = {}
        self._live_progress = rich.live.Live(self._generate_info_table())
        with self._live_progress:
            if pc is None:
                pc = multiprocessing.cpu_count()
            if pc < 2:
                for yt_dl in self.playlist:
                    self.download(yt_dl)
                return
            with multiprocessing.pool.ThreadPool(pc) as pool:
                pool.map(self.download, self.playlist)
            self._live_progress.update(f'{len(self.playlist)} downloaded.')

    def progress_callback(self, fn: str, total: int, downloaded: float, ratio: float, rate: float, eta: float):
        if ratio == 1.:
            if fn in self._table_data:
                del self._table_data[fn]
            return
        self._table_data[fn] = (
            f'\r{ratio:.2%}',
            f'{PrettyViewPrefix.from_bytes(downloaded)}/{PrettyViewPrefix.from_bytes(total)}',
            f'{PrettyViewPrefix.from_bytes(rate)}/s', PrettyViewPrefix.from_seconds(eta)
        )
        self._live_progress.update(self._generate_info_table())

    def _generate_info_table(self):
        _download_table = rich.table.Table(title=self.download_title,
                                           show_lines=True,
                                           highlight=True)
        for header in ('file name', '%', 'downloaded/total', 'rate', 'ETA'):
            _download_table.add_column(header, justify='center')
        for fn, v in self._table_data.items():
            _download_table.add_row(fn, *v)
        return _download_table


def with_api_key(func: Callable[[], _API_RET_TYPE]) -> Optional[_API_RET_TYPE]:
    for key in DownloadYTVideo.API_KEYS:
        pafy.set_api_key(key)
        try:
            return func()
        except pafy.util.GdataError:
            continue
