from __future__ import annotations

import datetime
import json
import os.path
import re
import time
from tempfile import TemporaryDirectory

from FastDub.FFMpeg import FFMpegWrapper

__all__ = ('LINE_REGEX',
           'Line',
           'parse', 'from_json', 'download_srt')

LINE_REGEX = re.compile(r'\n\n^\d+$\n', re.M)


class Line:
    __slots__ = ('ms', 'text', '_as_repr')

    class TimeLabel:
        __slots__ = ('start', 'duration', 'end', '_as_str')

        def __init__(self, start: float, end: float):
            self.duration = end - start
            self.start = start
            self.end = end
            self._as_str = f'<{start} --> {end}>'

        def __str__(self):
            return self._as_str

    def __init__(self, time_labels: tuple[datetime.time], text: str):
        self.ms: Line.TimeLabel = self.TimeLabel(*
                                                 [(label.hour * 3600000)
                                                  + (label.minute * 60000)
                                                  + (label.second * 1000)
                                                  + (label.microsecond / 1000)
                                                  for label in (time_labels[0], time_labels[-1])][:2]
                                                 )
        self.text: str = text
        self._as_repr = f'Line({self.ms}, {self.text!r})'

    def __repr__(self):
        return self._as_repr




def parse(text_or_file: str, skip_empty: bool = False) -> tuple[Line] | tuple:
    if os.path.isfile(text_or_file):
        fn, ext = os.path.splitext(text_or_file)
        if ext != '.srt':
            converted = f'{fn}.srt'
            FFMpegWrapper.convert('-i', text_or_file, converted)
            text_or_file = converted
        with open(text_or_file, encoding='UTF-8') as f:
            text = f.read()
    else:
        text = text_or_file
    subtitles = ()
    for i in LINE_REGEX.split(f'\n\n{text.lstrip()}')[1:]:
        times_text: list[str, str] = i.split('\n', 1)
        text = times_text[1].strip()
        if not text:
            continue
        subtitles += Line(tuple(datetime.time(k.hour, k.minute, k.second, k.microsecond) for k in
                                [datetime.datetime.strptime(j, '%H:%M:%S,%f') for j in
                                 times_text[0].split(' --> ', 1)]), text),
    return tuple(line for line in subtitles if line.text.strip()) if skip_empty else subtitles


