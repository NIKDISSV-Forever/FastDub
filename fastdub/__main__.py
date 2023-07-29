from __future__ import annotations

import argparse
import logging
import sys
from glob import iglob
from multiprocessing import cpu_count
from os import getcwd
from time import perf_counter

import rich.traceback

import fastdub.youtube
from fastdub import GlobalSettings, PrettyViewPrefix, dubber, translator, voicer, youtube
from fastdub.ffmpeg_wrapper import DefaultFFmpegParams
from fastdub.translator.subs_translate import SrtTranslate

__all__ = ('parse_args', 'main')
THREADS_MAY_NEED = youtube.SUPPORTED or translator.SUPPORTED

if hasattr(logging, '_nameToLevel'):
    def _get_logging_level_names() -> tuple[str]:
        # noinspection PyProtectedMember
        return *logging._nameToLevel,
elif sys.version_info >= (3, 11):
    def _get_logging_level_names() -> tuple[str]:
        return *logging.getLevelNamesMapping(),
else:
    def _get_logging_level_names() -> tuple[str]:
        return 'INFO',


class BooleanOptionalAction(argparse.Action):
    __slots__ = ()

    def __init__(self, option_strings, dest, default=None, type=None,
                 choices=None, required=False, help=None, metavar=None):
        _option_strings = (*option_strings,
                           *('--no-' + option_string[2:] if option_string.startswith('--') else
                             '-n-' + option_string[1:] if option_string.startswith('-') else option_strings
                             for option_string in option_strings))
        if help is not None and default is not None and default is not argparse.SUPPRESS:
            help += " (default: %(default)s)"
        super().__init__(option_strings=_option_strings, dest=dest, nargs=0, default=default, type=type,
                         choices=choices, required=required, help=help, metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            setattr(namespace, self.dest,
                    not (option_string.startswith('--no-') or option_string.startswith('-n-')))

    def format_usage(self):
        return ' | '.join(self.option_strings)


def _thread_count_type(tc: str) -> int:
    return int(cpu_count() * float(tc.removeprefix('*'))) if tc.startswith('*') else int(tc)


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
    arg_parser.add_argument('-ra', '--cleanup-audio', action=BooleanOptionalAction, default=True,
                            help='Remove result audio if video exists (default True)')
    arg_parser.add_argument('-ev', '--export-video', action=BooleanOptionalAction, default=True)
    arg_parser.add_argument('-l', '--language', default='ru',
                            help='Subtitles language (ru)')
    arg_parser.add_argument('-ll', '--loglevel', default='INFO', type=str.upper,
                            choices=_get_logging_level_names(),
                            help='Program log level')

    if THREADS_MAY_NEED:
        arg_parser.add_argument('-tc', '--threads-count', default=cpu_count(),
                                type=_thread_count_type,
                                help='Process count to download (pass to cpu count, < 2 to disable)\n'
                                     '\t*N = N * cpu count')

    input_group = arg_parser.add_argument_group('Input')
    input_group.add_argument('-i', '--input', default=getcwd(), required=True,
                             help=f"Input directory{('/YouTube Playlist/Video URL' if youtube.SUPPORTED else '')}.")
    input_group.add_argument('-vf', '--video-format', default='.mp4',
                             help='Video format (default: .mp4).')
    input_group.add_argument('-sf', '--subtitles-format', default='.srt',
                             help='Subtitles format (default: .srt).')

    exclude_input_group = arg_parser.add_argument_group('Input Exclude')
    exclude_input_group.add_argument('-En', '--exclude', type=iglob, nargs='+', default=(),
                                     help='Exclude <name> (glob)')
    exclude_input_group.add_argument('-Eu', '--exclude-underscore', default=True,
                                     help='Exclude files starts with underscore')

    ducking_group = arg_parser.add_argument_group('Audio Ducking')
    ducking_group.add_argument('-sc', '--sidechain', action=BooleanOptionalAction, default=True,
                               help='Enable audio side chain compress (ducking)')
    ducking_group.add_argument('-sc-args', '--sidechain-ffmpeg-params', default=DefaultFFmpegParams.sidechain_args,
                               help=f'sidechain FFmpeg parameters (default {DefaultFFmpegParams.sidechain_args!r})')
    ducking_group.add_argument('-sc-lvl', '--sidechain-level-sc', type=float, default=.8,
                               help='Set sidechain gain. Range is between 0.015625 and 64. (default 0.8)')

    voicer_group = arg_parser.add_argument_group('Voicer')
    voicer_group.add_argument('-v', '--voice', type=str.lower, choices=voicer.VOICES_NAMES.keys(),
                              help='SAPI voice for voice acting.')
    voicer_group.add_argument('-a', '--align', default=2., type=float,
                              help='Audio fit align (divisor)'
                                   '\n\t1 = right'
                                   '\n\t2 = center (default)')
    voicer_group.add_argument('-v-set-a', '--voice-set-anchor', default='!:',
                              help='Anchor indicating voice actor change (default "!:")')

    ffmpeg_group = arg_parser.add_argument_group('FFmpeg Output')
    ffmpeg_group.add_argument('-fll', '--ffmpeg-loglevel', default='panic',
                              choices=(
                                  'trace', 'debug', 'verbose', 'info', 'warning', 'error', 'fatal', 'panic', 'quiet'),
                              help='FFmpegWrapper loglevel')
    ffmpeg_group.add_argument('-y', '--confirm', action=BooleanOptionalAction, default=True,
                              help="Don't ask for confirmation")
    ffmpeg_group.add_argument('-af', '--audio-format', default='wav',
                              help='Out audio files format (default wav)')
    ffmpeg_group.add_argument('-wm', '--watermark', default='',
                              help='Add watermark to output video')

    output_group = arg_parser.add_argument_group('Terminal Output')
    output_group.add_argument('-tb', '--traceback', action=BooleanOptionalAction, default=False,
                              help='Show debug traceback')

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
        yt_search_group.add_argument('-yts-rg', '--youtube-search-region', default='US',
                                     help='Sets the result region. Defaults to "US".')

    if fastdub.youtube.yt_upload.SUPPORTED:
        ytu_group = arg_parser.add_argument_group('YouTube Upload')
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
        translate_group.add_argument('--rewrite-srt', action=BooleanOptionalAction, default=False,
                                     help='Rewrite input subtitles files.\n'
                                          'If not, add "_" to the beginning of the original subtitle file.')
        translate_group.add_argument('-ts', '--translate-service',
                                     default='google',
                                     choices=translator.SERVICES,
                                     help='Subtitle translation service. (default google)')
    return arg_parser.parse_args()


def banner():
    rich.print('[b][i]FastDub[/][/]\n'
               'https://github.com/NIKDISSV-Forever/FastDub')


def main():
    args = parse_args()

    if args.traceback:
        rich.traceback.install(show_locals=True)
    else:
        rich.traceback.install(extra_lines=0, word_wrap=True)
    logging.basicConfig(format='%(levelname)s: [%(asctime)s] %(message)s')
    logging.getLogger().setLevel(args.loglevel)

    remove_cache = args.remove_cache
    if remove_cache == 1:
        dubber.VOICER.cleanup()

    GlobalSettings.watermark = args.watermark
    DefaultFFmpegParams.ffmpeg_log_level = args.ffmpeg_loglevel

    total_time = 0
    if args.confirm:
        DefaultFFmpegParams.args += '-y',
        total_time = perf_counter()

    if THREADS_MAY_NEED:
        GlobalSettings.threads_count = args.threads_count

    if youtube.SUPPORTED and args.youtube:
        query: str = args.input
        if args.youtube_search and not query.startswith('?'):
            query = f'?{query.strip()}'
        youtube.downloader.DownloadYTVideo.API_KEYS |= {*args.api_keys}
        downloader = youtube.downloader.DownloadYTVideo(query,
                                                        args.language,
                                                        args.youtube_search_limit, args.youtube_search_limit, )
        downloader.multiprocessing_download()
        args.input = downloader.save_dir

    video_format = video_format if (video_format := args.video_format).startswith('.') else f'.{video_format}'
    subtitles_format = (
        subtitles_format if (subtitles_format := args.subtitles_format).startswith('.') else f'.{subtitles_format}')
    audio_format: str = args.audio_format.removeprefix('.')

    videos = dubber.Dubber.collect_videos(args.input, args.exclude_underscore, (*sum(args.exclude, []),))

    if translator.SUPPORTED:
        translate_service = translator.get_service_by_name(args.translate_service)
        if args.translate:
            SrtTranslate(args.language, translate_service, args.rewrite_srt).translate_dir(videos, subtitles_format)
    else:
        translate_service = None

    dubber.Dubber(args.voice, args.language, audio_format,
                  args.sidechain, args.sidechain_level_sc, args.sidechain_ffmpeg_params,
                  args.align,
                  args.cleanup_audio, args.export_video
                  ).dub_dir(videos, video_format, subtitles_format)

    if remove_cache == 2:
        voicer.Voicer().cleanup()

    if fastdub.youtube.yt_upload.SUPPORTED and args.youtube_upload:
        fastdub.youtube.yt_upload.uploader.Uploader(args.privacy_status,
                                                    translator.SUPPORTED and args.youtube_upload_translate,
                                                    translate_service
                                                    ).upload(args.input)

    if total_time:
        logging.info(f'total time {PrettyViewPrefix.from_seconds(perf_counter() - total_time)}')


if __name__ == '__main__':
    banner()
    main()
