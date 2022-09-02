from __future__ import annotations

import argparse
import glob
import multiprocessing
import os
from math import inf
from time import perf_counter

import fastdub.youtube
from fastdub import dubber, voicer
from fastdub import translator
from fastdub import youtube
from fastdub.ffmpeg_wrapper import FFMpegWrapper
from fastdub.translator.subs_translate import SrtTranslate


# noinspection PyTypeChecker
def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser('fastdub',
                                         description='fastdub is a tool for dubbing videos by subtitle files.',
                                         formatter_class=argparse.RawTextHelpFormatter)

    arg_parser.add_argument('-rc', '--remove-cache', default=2, type=int, choices=(0, 1, 2),
                            help='Remove all cache (_cached_texts directory) files\n'
                                 '\t0 - No remove cache\n'
                                 '\t1 - Delete cache before voice acting\n'
                                 '\t2 - Delete cache after voice acting (default)')
    arg_parser.add_argument('-rf', '--cleanup-level', default=1,
                            help='Cleanup level'
                                 '\t0 = No removing any files\n'
                                 '\t> 0 remove audio from video (default)\n'
                                 '\t> 1 = remove dubbed audio if video exists\n'
                                 '\t> 2 = remove dubbed cache files')

    arg_parser.add_argument('-l', '--language', default='ru',
                            help='Subtitles language (ru)')

    if youtube.SUPPORTED or translator.SUPPORTED:
        arg_parser.add_argument('-tc', '--threads-count', default=multiprocessing.cpu_count(),
                                type=lambda i: int(multiprocessing.cpu_count() * float(i.lstrip('*')))
                                if i.startswith('*') else int(i),
                                help='Process count to download (pass to cpu count, < 2 to disable)\n'
                                     '\t*N = N * cpu count')

    input_group = arg_parser.add_argument_group('Input')
    input_group.add_argument('-i', '--input', type=str, default=os.getcwd(), required=True,
                             help=f"Input directory{('/YouTube Playlist/Video URL' if youtube.SUPPORTED else '')}.")
    input_group.add_argument('-vf', '--video-format', default='.mp4',
                             help='Video format (default .mp4).')
    input_group.add_argument('-sf', '--subtitles-format', default='.srt',
                             help='Subtitles format (default .srt).')

    exclude_input_group = input_group.add_argument_group('Exclude Input')
    exclude_input_group.add_argument('-En', '--exclude', type=glob.glob, nargs='+', default=(),
                                     help='Exclude <name> (glob)')
    exclude_input_group.add_argument('-Eu', '--exclude-underscore', default=True,
                                     help='Exclude files starts with underscore')

    ducking_group = arg_parser.add_argument_group('Audio Ducking')
    ducking_group.add_argument('-sc', '--sidechain', action=argparse.BooleanOptionalAction, default=True,
                               help='Enable audio side chain compress (ducking)')
    ducking_group.add_argument('-sc-msl', '--min-silence-len', '--attack', default=100, type=int,
                               help='Minimum silence length in ms (default 100)')
    ducking_group.add_argument('-sc-st', '--silence-thresh', default=-inf, type=float,
                               help='Silence threshold in dB')
    ducking_group.add_argument('-sc-gdo', '--gain-during-overlay', default=-11, type=int,
                               help='Gain during overlay in dB (-11)')

    voicer_group = arg_parser.add_argument_group('Voicer')
    voicer_group.add_argument('-v', '--voice', type=str.lower, choices=voicer.VOICES_NAMES.keys(),
                              help='SAPI voice for voice acting.')
    voicer_group.add_argument('-a', '--align', default=2., type=float,
                              help='Audio fit align\n'
                                   '\t1 = right\n'
                                   '\t2 = center (default)')

    ffmpeg_group = arg_parser.add_argument_group('FFMpeg Output')
    ffmpeg_group.add_argument('-ll', '--loglevel', default='panic',
                              choices=(
                                  'trace', 'debug', 'verbose', 'info', 'warning', 'error', 'fatal', 'panic', 'quiet'),
                              help='FFMpegWrapper loglevel')
    ffmpeg_group.add_argument('-y', '--confirm', action=argparse.BooleanOptionalAction, default=True,
                              help="Don't ask for confirmation")
    if youtube.SUPPORTED:
        yt_group = arg_parser.add_argument_group('YouTube')
        yt_group.add_argument('-yt', '--youtube', action='store_true', default=False)
        yt_group.add_argument('-ak', '--api-keys', nargs='+', default=(), help='Youtube API key/s')

        yt_search_group = arg_parser.add_argument_group('YouTube Search')
        yt_search_group.add_argument('-yts', '--youtube-search', action='store_true', default=False,
                                     help='The input data is a query for searching on YouTube.'
                                          ' (Adds "?" at the start of input)')
        yt_search_group.add_argument('-yts-l', '--youtube-search-limit', type=int, default=20,
                                     help='Sets limit to the number of results. Defaults to 20.')
        yt_search_group.add_argument('-yts-rg', '--youtube-search-region', type=str, default='US',
                                     help='Sets the result region. Defaults to "US".')

    if fastdub.youtube.yt_upload.SUPPORTED:
        ytu_group = arg_parser.add_argument_group('YouTube yt_upload')
        ytu_group.add_argument('-ytu', '--youtube-upload', action='store_true', default=False,
                               help='yt_upload video to YouTube channel after voice acting.')
        ytu_group.add_argument('-ytu-ps', '--privacy-status',
                               default=fastdub.youtube.yt_upload.VALID_PRIVACY_STATUSES[0],
                               choices=fastdub.youtube.yt_upload.VALID_PRIVACY_STATUSES,
                               help='Video privacy status (If not private, errors are possible)')
        if translator.SUPPORTED:
            ytu_group.add_argument('-ytu-t', '--youtube-upload-translate', action='store_true', default=False,
                                   help='Translate title and description on upload. '
                                        '(+ Arguments from translate argument group)')

    if translator.SUPPORTED:
        translate_group = arg_parser.add_argument_group('Translate')
        translate_group.add_argument('-tr', '--translate', action='store_true', default=False,
                                     help='Translate input subtitles files')
        translate_group.add_argument('--rewrite-srt', action=argparse.BooleanOptionalAction, default=False,
                                     help='Rewrite input subtitles files.\n'
                                          'If not, add "_" to the beginning of the original subtitle file.')
        translate_group.add_argument('-ts', '--translate-service', type=translator.get_service_by_name,
                                     default='google',
                                     choices=translator.SERVICES,
                                     help='Subtitle translation service. (default google)')

    return arg_parser.parse_args()


def main():
    args = parse_args()
    remove_cache = args.remove_cache
    if remove_cache == 1:
        dubber.VOICER.cleanup()

    FFMpegWrapper.DEFAULT_FFMPEG_LOG_LEVEL = args.loglevel

    total_time = 0.
    if args.confirm:
        FFMpegWrapper.DEFAULT_ARGS += '-y',
        total_time = perf_counter()

    if youtube.SUPPORTED and args.youtube:
        query: str = args.input
        if args.youtube_search and not query.startswith('?'):
            query = f'?{query.strip()}'
        youtube.downloader.DownloadYTVideo.API_KEYS |= {*args.api_keys}
        downloader = youtube.downloader.DownloadYTVideo(query,
                                                        args.language,
                                                        args.youtube_search_limit, args.youtube_search_limit, )
        downloader.multiprocessing_download(args.threads_count)
        args.input = downloader.save_dir

    video_format = video_format if (video_format := args.video_format).startswith('.') else f'.{video_format}'
    subtitles_format = (
        subtitles_format if (subtitles_format := args.subtitles_format).startswith('.') else f'.{subtitles_format}')

    videos = dubber.Dubber.collect_videos(args.input, args.exclude_underscore, (*sum(args.exclude, []),))

    if translator.SUPPORTED and args.translate:
        SrtTranslate(args.language, args.translate_service, args.rewrite_srt, args.threads_count
                     ).translate_dir(videos, subtitles_format)

    dubs = dubber.Dubber(args.voice, args.language, args.sidechain, args.min_silence_len, args.silence_thresh,
                         args.gain_during_overlay, args.align)

    dubs.dub_dir(videos, video_format, subtitles_format)

    if remove_cache == 2:
        voicer.Voicer().cleanup()

    if fastdub.youtube.yt_upload.SUPPORTED and args.youtube_upload:
        translate = False
        translate_serv = None
        if translator.SUPPORTED:
            translate = args.youtube_upload_translate
            translate_serv = args.translate_service
        fastdub.youtube.yt_upload.uploader.Uploader(args.privacy_status, translate, translate_serv).upload(args.input)

    if total_time:
        print(f'Total time: {perf_counter() - total_time:,g} s.')


if __name__ == '__main__':
    main()
