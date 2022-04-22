import json
import math
import os.path
import tempfile
import time

import download_youtube_subtitle.main


def _float_to_srt_time_format(d: float) -> str:
    fraction, whole = math.modf(d)
    return f"{time.strftime('%H:%M:%S,', time.gmtime(whole))}{f'{fraction:.3f}'.replace('0.', '')}"


def _from_json(json_: dict[str, dict[str, str]]) -> str:
    srt_s = ''
    for i, el in enumerate(json_.get('translation', ()), 1):
        # noinspection PyTypeChecker
        srt_s += (f"\n\n{i}\n{_float_to_srt_time_format((start := int(el['start'])) / 1000.)}"
                  " --> "
                  f"{_float_to_srt_time_format((start + int(el['dur'])) / 1000.)}\n{el['text']}")
    return srt_s.lstrip('\n')


def download_srt(video_id: str, lang: str, fp: str):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_name = os.path.join(tmp, 'target.json')
        download_youtube_subtitle.main.main(video_id, lang, output_file=tmp_name, to_json=True)
        with open(tmp_name, encoding='UTF-8') as f:
            _json: dict[str, dict] = json.load(f)
    with open(fp, 'w', encoding='UTF-8') as srt_f:
        srt_f.write(_from_json(_json))
