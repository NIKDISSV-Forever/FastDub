from __future__ import annotations

import multiprocessing.pool
import os.path
from functools import lru_cache
from typing import Callable

from tqdm import tqdm

from fastdub import GlobalSettings, subtitles

__all__ = ('SrtTranslate',)


class SrtTranslate:
    __slots__ = ('language', 'rewrite', 'threads_count', 'service', '_pb')

    def __init__(self, language: str, service: Callable, rewrite: bool = False, threads_count: int = None):
        self.language = language
        self.service = service
        self.rewrite = rewrite
        self.threads_count = threads_count or GlobalSettings.threads_count

    @lru_cache
    def translate_line(self, text: str) -> str:
        return self.service(text, to_language=self.language)

    def translate_all(self, input_srt: str, output_srt: str):
        parsed = subtitles.parse(input_srt)
        for line in parsed:
            line.text = line.text.strip()
        _pb = tqdm(parsed, 'Translating', len(parsed), unit='line', **GlobalSettings.tqdm_kwargs)
        if self.threads_count > 1:
            def handler(line: subtitles.Line):
                line.text = self.translate_line(line.text)
                _pb.update()

            with multiprocessing.pool.ThreadPool(self.threads_count) as pool:
                pool.map(handler, parsed)
        else:
            for line in _pb:
                line.text = self.translate_line(line.text)
        with open(output_srt, 'w', encoding='UTF-8') as f:
            f.write(subtitles.unparse(parsed))

    def translate_dir(self, files: dict[str, dict[str, str]], subtitles_format: str):
        for fn, exts in files.items():
            inp = out = exts[subtitles_format]
            if not self.rewrite:
                inp = os.path.join(*os.path.split(inp)[:-1], f'_{os.path.basename(inp)}')
                if os.path.isfile(inp):
                    os.remove(inp)
                os.rename(out, inp)
            self.translate_all(inp, out)
