"""Convert JSON file with auto-generated subtitles from https://www.veed.io to .srt file"""
import argparse
import json
from pathlib import Path

from fastdub.subtitles import ms_to_srt_time


def from_veed_json(json_file: Path):
    with json_file.open('r', encoding='UTF-8') as f:
        jls = json.load(f)
    (json_file.parent / f'{json_file.stem}.srt').write_text('\n\n'.join(
        f"{i}\n{ms_to_srt_time(v['from'] * 1000)} --> {ms_to_srt_time(v['to'] * 1000)}\n"
        f"{' '.join(t['value'] for t in v['words'])}"
        for i, v in enumerate((*(jls['data']['edit']['subtitles']['tracks'].values()),)[0]['items'].values(), 1)
    ), 'UTF-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json_file', type=Path)
    args = parser.parse_args()
    from_veed_json(args.json_file)


if __name__ == '__main__':
    main()
