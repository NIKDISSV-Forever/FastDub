from __future__ import annotations

import logging
import os.path
import shutil
from pathlib import Path
from typing import Sequence

import rich.align
from tqdm import tqdm

from fastdub import audio, subtitles, voicer, GlobalSettings
from fastdub.audio import AudioSegment, calc_speed_change_ffmpeg_arg
from fastdub.ffmpeg_wrapper import FFMpegWrapper

__all__ = ('Dubber', 'VOICER')

from fastdub.subtitles import Line, TimeLabel

VOICER = voicer.Voicer()


class Dubber:
    __slots__ = (
        'fit_align', 'language', 'audio_format',
        'cleanup_audio', 'export_video',
        'ducking',
        'sidechain_level_sc', 'sidechain_ffmpeg_params'
    )

    def __init__(self, voice: str, language: str, audio_format: str,
                 ducking: bool, sidechain_level_sc: float, sidechain_ffmpeg_params: str,
                 fit_align: float = 2., cleanup_audio: bool = True, export_video: bool = True):
        self.language = language
        self.audio_format = audio_format
        self.fit_align = fit_align
        if voice:
            VOICER.set_voice(voice)

        self.ducking = ducking
        self.sidechain_level_sc = sidechain_level_sc
        self.sidechain_ffmpeg_params = sidechain_ffmpeg_params

        self.cleanup_audio = cleanup_audio
        self.export_video = export_video

    @staticmethod
    def collect_videos(path_to_files: str, skip_starts_underscore: bool = True,
                       exclude_files: Sequence[str] = frozenset()):
        path_to_files = os.path.abspath(path_to_files)
        videos = {}
        for file in os.listdir(path_to_files):
            if file in exclude_files:
                continue
            absfile = os.path.join(path_to_files, file)
            if not os.path.isfile(absfile) or skip_starts_underscore and file.startswith('_'):
                continue
            filename, ext = os.path.splitext(file)
            if videos.get(filename):
                videos[filename][ext] = absfile
                continue
            videos[filename] = {ext: os.path.join(path_to_files, file)}
        return videos

    def dub_dir(self, videos: dict[str, dict[str, str]], video_format: str, subtitles_format: str):
        for fn, exts in videos.items():
            self.dub_one(fn, exts.get(video_format), exts.get(subtitles_format))

    def dub_one(self, fn: str, target_vid: str, target_sub: str, cleanup_audio: bool = None, export_video: bool = None):
        if target_vid is None and target_sub is None:
            return
        if cleanup_audio is None:
            cleanup_audio = self.cleanup_audio
        if export_video is None:
            export_video = self.export_video

        logging.info(f'start voice file {fn!r}')
        result_dir = Path(target_sub).parent / '_result'
        result_dir.mkdir(exist_ok=True)
        out_audio_base = result_dir / f'{fn}_{self.language}.{self.audio_format}'

        subs = subtitles.parse(target_sub)
        default_right_border = 0
        if target_vid and subs:
            default_right_border = FFMpegWrapper.get_video_duration_ms(target_vid)
        default_right_border = max(default_right_border, end := subs[-1].ms.end)
        subs += Line(TimeLabel(default_right_border, end, end - default_right_border)),

        progress_total = len(subs) - 1

        fit_align = self.fit_align
        audio_format = self.audio_format

        working_dir = result_dir / '_working_dir'
        working_dir.mkdir(exist_ok=True)

        filenames: tuple[str] = *map(
            str(working_dir / ('{0:0>%i}.%s' % (len(str(progress_total)), audio_format))).format, range(len(subs))),

        filename_sub = *zip(filenames_striped := filenames[:-1], subs[:-1]),
        cached_tts = [VOICER.voice(line.text) for fn, line in tqdm(filename_sub,
                                                                   desc='TTS',
                                                                   total=progress_total, unit='line',
                                                                   dynamic_ncols=True)]

        total_duration_ms = 0
        for pos, ((tts_fn, line), cached) in tqdm(
                enumerate(zip(filename_sub, cached_tts), 1),
                desc='Fitting',
                total=progress_total, unit='line',
                **GlobalSettings.tqdm_kwargs):
            ms = line.ms
            new_audio = audio.fit(
                AudioSegment.from_file(cached, 'wav'),
                ms.start - total_duration_ms,
                ms.duration,
                subs[pos].ms.start - ms.end,
                fit_align
            )
            total_duration_ms += new_audio.duration_ms
            new_audio.export(tts_fn, audio_format)
        with open(list_file := working_dir / 'list.txt', 'w') as f:
            f.writelines(f"file '{fn}'\n" for fn in filenames_striped)
        max_duration = subs[-1].ms.end

        ffmpeg_concat_args = ()
        if total_duration_ms > max_duration:
            change_speed = total_duration_ms / max_duration
            logging.info(f'changing audio speed {change_speed:g}')
            ffmpeg_concat_args += '-af', calc_speed_change_ffmpeg_arg(change_speed)
        else:
            ffmpeg_concat_args += '-c', 'copy'

        temp_audio_file = str(out_audio_base.with_stem(f'_{out_audio_base.stem}'))
        logging.info('concatenating parts...')
        FFMpegWrapper.convert('-f', 'concat', '-safe', '0', '-i', list_file, *ffmpeg_concat_args,
                              temp_audio_file)
        cur_audio = audio.AudioSegment.from_file(temp_audio_file)
        shutil.rmtree(working_dir, ignore_errors=True)

        if total_duration_ms != max_duration:
            cur_audio = audio.AudioSegment.silent(
                min(max_duration - total_duration_ms, subs[0].ms.start)
            ) + cur_audio

        result_out_audio = str(out_audio_base)
        if target_vid:
            cur_audio.export(temp_audio_file, format='wav')
            if self.ducking:
                logging.info('sidechain')
                FFMpegWrapper.sidechain(target_vid,
                                        temp_audio_file,
                                        result_out_audio,
                                        self.sidechain_level_sc,
                                        self.sidechain_ffmpeg_params)
            else:
                logging.info('amix')
                FFMpegWrapper.amix(target_vid, temp_audio_file, out=result_out_audio)
                # audio.AudioSegment.from_file(target_vid).overlay(cur_audio).export(result_out_audio)
            if export_video:
                FFMpegWrapper.save_result_data(target_vid, result_out_audio, target_sub,
                                               result_dir / f'{fn}_{self.language}.mkv')
                if cleanup_audio:
                    os.remove(result_out_audio)
        else:
            cur_audio.export(result_out_audio)
        os.remove(temp_audio_file)
