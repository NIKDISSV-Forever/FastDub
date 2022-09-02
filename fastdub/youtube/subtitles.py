from __future__ import annotations

import json
import os.path
import time
from math import modf
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

__all__ = ('download_srt',)

import download_youtube_subtitle.main as down_yt_subs


def find_caption_num(video_id: str, lang_code: str) -> int | None:
    video_id = down_yt_subs.parseVideoID(video_id)[0]
    try:
        caption_tracks = down_yt_subs.get_tracks_title(video_id)[0]
    except Exception:
        down_yt_subs.perr("can't retrive caption, ", " for detail")
        raise
    for i, caption in enumerate(caption_tracks):
        if caption.get('languageCode') == lang_code:
            return i


subs_download = down_yt_subs.main


def _float_to_srt_time_format(d: float) -> str:
    fraction, whole = modf(d)
    return f"{time.strftime('%H:%M:%S,', time.gmtime(whole))}{f'{fraction:.3f}'.replace('0.', '')}"


def _from_json(translation: Iterable[dict[str, str]]) -> str:
    return '\n\n'.join(
        f"{i}\n{_float_to_srt_time_format((start := int(el['start'])) / 1000.)}"
        " --> "
        f"{_float_to_srt_time_format((start + int(el['dur'])) / 1000.)}\n{el['text']}"
        for i, el in enumerate(translation, 1))


def download_srt(video_id: str, lang: str, fp: str | Path):
    with TemporaryDirectory() as tmp:
        tmp_name = os.path.join(tmp, 'out.srt.json')
        cap_num = find_caption_num(video_id, lang)
        if cap_num is None:
            subs_download(video_id, lang, output_file=tmp_name, to_json=True)
        else:
            subs_download(video_id, False, caption_num_second=cap_num,
                          output_file=tmp_name, to_json=True)
        with open(tmp_name, encoding='UTF-8') as f:
            _json: dict[str, list[dict[str, str]]] = json.load(f)
    with open(fp, 'w', encoding='UTF-8') as srt_f:
        srt_f.write(_from_json(_json.get('translation', ())))
