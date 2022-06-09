import multiprocessing.pool
import os.path
from functools import cache
from pathlib import Path

import tqdm

from FastDub import Subtitles
from FastDub.Translator import *


class SrtTranslate:
    __slots__ = ('language', 'rewrite', 'threads_count', 'service', '_pb')

    def __init__(self, language: str, service: str, rewrite: bool = False, threads_count: int = None):
        self.language = language
        self.service = getattr(translators, service)
        self.rewrite = rewrite
        self.threads_count = threads_count or multiprocessing.cpu_count()

    def translate_all(self, input_srt: str, output_srt: str):
        parsed = Subtitles.parse(input_srt)
        _pb = tqdm.tqdm(parsed, 'Translating', len(parsed), unit='line', dynamic_ncols=True)
        if self.threads_count > 1:
            def handler(line: Subtitles.Line):
                line.text = self.translate_line(line.text)
                _pb.update()

            with multiprocessing.pool.ThreadPool(self.threads_count) as pool:
                pool.map(handler, parsed)
        else:
            for line in _pb:
                line.text = self.translate_line(line.text.strip())
        with open(output_srt, 'w', encoding='UTF-8') as f:
            f.write(Subtitles.unparse(parsed))

    @cache
    def translate_line(self, text: str):
        return self.service(text, to_language=self.language)

    def translate_dir(self, files: dict[str, dict[str, str]], subtitles_format: str):
        for fn, exts in files.items():
            inp = out = exts[subtitles_format]
            if not self.rewrite:
                inp = os.path.join(*os.path.split(inp)[:-1], f'_{os.path.basename(inp)}')
                if os.path.isfile(inp):
                    os.remove(inp)
                os.rename(out, inp)
            self.translate_all(inp, out)
