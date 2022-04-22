from __future__ import annotations

import argparse
import os
import time
from math import inf

from FastDub import Dubber, Voicer
from FastDub import YT
from FastDub.FFMpeg import FFMpegWrapper
from FastDub.YT.Downloader import DownloadYTVideo


def main():
    arg_parser = argparse.ArgumentParser('FastDub',
                                         description='FastDub is a tool for dubbing videos by subtitle files.',
                                         formatter_class=argparse.RawTextHelpFormatter)

    arg_parser.add_argument('-rc', '--remove-cache', action='store_true',
                            help='Remove all cache files')
    arg_parser.add_argument('-rf', '--cleanup-level', default=1,
                            help='Cleanup level'
                                 '\t0 = No removing any files\n'
                                 '\t> 0 remove audio from video (default)\n'
                                 '\t> 1 = remove dubbed audio if video exists\n'
                                 '\t> 2 = reomve dubbed cache files')

    input_group = arg_parser.add_argument_group('Input')
    input_group.add_argument('-i', '--input', type=str, required=True,
                             help='Input directory.')
    input_group.add_argument('-vf', '--video-format', default='.mp4',
                             help='Video format (default .mp4).')
    input_group.add_argument('-sf', '--subtitles-format', default='.srt',
                             help='Subtitles format (default .srt).')

    exclude_input_group = input_group.add_argument_group('Exclude Input')
    exclude_input_group.add_argument('-En', '--exclude', nargs='+', default=(),
                                     help='Exclude <name>')
    exclude_input_group.add_argument('-Eu', '--exclude-underscore', default=True,
                                     help='Exclude files starts with underscore')

    ducking_group = arg_parser.add_argument_group('Audio Ducking')
    ducking_group.add_argument('-sc', '--sidechain', action=argparse.BooleanOptionalAction, default=True,
                               help='Enable audio side chain compress (ducking)')
    ducking_group.add_argument('-sc-msl', '--min-silence-len', '--attack', default=100, type=int,
                               help='Minimum silence length in ms (default 100)')
    ducking_group.add_argument('-sc-st', '--silence-thresh', default=-inf, type=float,
                               help='Silence threshold in dB')
    ducking_group.add_argument('-sc-gdo', '--gain-during-overlay', default=-10, type=int,
                               help='Gain during overlay in dB')

    voicer_group = arg_parser.add_argument_group('Voicer')
    voicer_group.add_argument('-v', '--voice', choices=Voicer.VOICES_NAMES.keys(),
                              help='Voice')
    voicer_group.add_argument('-a', '--align', default=2., type=float,
                              help='Audio fit align\n'
                                   '\t1 = right\n'
                                   '\t2 = center (default)')

    ffmpeg_group = arg_parser.add_argument_group('FFMpeg Output')
    ffmpeg_group.add_argument('-ll', '--loglevel', default='panic',
                              help='FFMpegWrapper loglevel')
    ffmpeg_group.add_argument('-y', '--confirm', action=argparse.BooleanOptionalAction, default=True,
                              help="Don't ask for confirmation")

    if YT.SUPPORTED:
        yt_group = arg_parser.add_argument_group('Youtube')
        yt_group.add_argument('-yt', '--youtube', action=argparse.BooleanOptionalAction, default=True)
        yt_group.add_argument('-l', '--language', default='ru',
                              help='Subtitles language (ru)')
        yt_group.add_argument('-ak', '--api-keys', nargs='+', default=(), help='Youtube API key/s')
        yt_group.add_argument('-pc', '--process-count', type=int,
                              help='Process count to download (pass to cpu count, < 2 to disable)')

    args = arg_parser.parse_args()

    FFMpegWrapper.DEFAULT_FFMPEG_LOG_LEVEL = args.loglevel
    if args.remove_cache:
        Voicer.Voicer().cleanup()

    total_time = 0.
    if args.confirm:
        FFMpegWrapper.DEFAULT_ARGS += '-y',
        total_time = time.perf_counter()

    if YT.SUPPORTED and args.youtube:
        downloader = DownloadYTVideo(args.input, args.language, args.api_keys)
        downloader.multiprocessing_download(args.process_count)
        args.input = downloader.save_dir

    dubber = Dubber.Dubber(args.voice, args.sidechain, args.min_silence_len, args.silence_thresh,
                           args.gain_during_overlay, args.video_format, args.subtitles_format)
    dubber.dub_dir(args.input, args.exclude_underscore, args.exclude)

    if total_time:
        print(f'Total time: {time.perf_counter() - total_time}s')


if __name__ == '__main__':
    main()
