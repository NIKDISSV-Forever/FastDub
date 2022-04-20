from __future__ import annotations

import argparse
from math import inf

from FastDub import Dubber, Voicer
from FastDub.FFMpeg import FFMpegWrapper


def main():
    arg_parser = argparse.ArgumentParser('FastDub',
                                         description="FastDub is a tool for dubbing videos by subtitle files.",
                                         formatter_class=argparse.RawTextHelpFormatter)

    input_group = arg_parser.add_argument_group("Input")
    input_group.add_argument("-i", "--input", help="Input file or directory.", required=True)
    input_group.add_argument('-vf', '--video-format', help="Video format (default .mp4).", default=".mp4")
    input_group.add_argument('-sf', '--subtitles-format', help="Subtitles format (default .srt).", default=".srt")

    exclude_input_group = input_group.add_argument_group("Exclude Input")
    exclude_input_group.add_argument('-En', '--exclude', nargs='+', default=(), help="Exclude <name>")
    exclude_input_group.add_argument("-Eu", "--exclude-underscore", default=True,
                                     help="Exclude files starts with underscore")

    ducking_group = arg_parser.add_argument_group("Audio Ducking")
    ducking_group.add_argument('-dk', "--ducking", action=argparse.BooleanOptionalAction, default=True,
                               help="Enable audio ducking")
    ducking_group.add_argument('-dk-msl', "--min-silence-len", default=100, type=int,
                               help="Minimum silence length in ms (default 100)")
    ducking_group.add_argument('-dk-st', "--silence-thresh", default=-inf, type=float, help="Silence threshold in dB")
    ducking_group.add_argument('-dk-gdo', "--gain-during-overlay", default=-10, type=int,
                               help="Gain during overlay in dB")

    voicer_group = arg_parser.add_argument_group("Voicer")
    voicer_group.add_argument("-v", "--voice", choices=Voicer.VOICES_NAMES.keys(), help="Voice")
    voicer_group.add_argument("-a", "--align", default=2., type=float,
                              help="Audio fit align\n"
                                   "\t1 = right\n"
                                   "\t2 = center")

    output_group = arg_parser.add_argument_group("Output")
    output_group.add_argument("-ll", "--loglevel", help="FFMpegWrapper loglevel", default='panic')
    output_group.add_argument('-y', '--yes', action='store_true', help="Don't ask for confirmation")
    output_group.add_argument('-rf', '--cleanup-level', default=1,
                              help="Cleanup level (0 = No removing any files\n"
                                   "\t> 0 remove audio from video (default)\n"
                                   "\t> 1 = remove dubbed audio if video exists)\n"
                                   "\t> 2 = reomve dubbed cache files")

    arg_parser.add_argument('-rc', '--remove-cache', action='store_true', help="Remove all cache files")

    args = arg_parser.parse_args()

    if args.remove_cache:
        Voicer.Voicer().cleanup()

    FFMpegWrapper.DEFAULT_FFMPEG_LOG_LEVEL = args.loglevel
    if args.yes:
        FFMpegWrapper.DEFAULT_ARGS += '-y',

    dubber = Dubber.Dubber(args.voice, args.ducking, args.min_silence_len, args.silence_thresh,
                           args.gain_during_overlay, args.video_format, args.subtitles_format)
    dubber.dub_dir(args.input, args.exclude_underscore, args.exclude)


if __name__ == '__main__':
    main()
