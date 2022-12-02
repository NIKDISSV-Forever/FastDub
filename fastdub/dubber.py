from __future__ import annotations

import os.path
from contextlib import closing
from pathlib import Path
from typing import Sequence

import rich.align
from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm

from fastdub import audio, subtitles, voicer
from fastdub.ffmpeg_wrapper import FFMpegWrapper

__all__ = ('Dubber', 'VOICER')

VOICER = voicer.Voicer()


class Dubber:
    __slots__ = (
        'fit_align', 'language', 'audio_format',
        'ducking', 'min_silence_len', 'silence_thresh',
        'gain_during_overlay',
        'cleanup_level'
    )

    def __init__(self, voice: str, language: str, audio_format: str,
                 ducking: bool, min_silence_len: int, silence_thresh: float, gain_during_overlay: int,
                 fit_align: float = 2., cleanup_level: int = 2):
        self.language = language
        self.audio_format = audio_format
        self.fit_align = fit_align
        if voice:
            VOICER.set_voice(voice)

        self.ducking = ducking
        self.min_silence_len = min_silence_len
        self.silence_thresh = silence_thresh
        self.gain_during_overlay = gain_during_overlay

        self.cleanup_level = cleanup_level

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
            target_vid = exts.get(video_format)
            target_sub = exts.get(subtitles_format)

            if not target_vid:
                raise FileNotFoundError(fn + video_format)
            if not target_sub:
                raise FileNotFoundError(fn + subtitles_format)

            self.dub_one(fn, target_vid, target_sub)

    def dub_one(self, fn: str, target_vid: str, target_sub: str, cleanup_audio: bool = None):
        if target_vid is target_sub is None:
            return
        rich.print(rich.align.Align(fn, 'center'))
        subs = subtitles.parse(target_sub)

        default_right_border = 0
        if target_vid and subs:
            video_clip: VideoFileClip
            with closing(VideoFileClip(target_vid, audio=False)) as video_clip:
                default_right_border = video_clip.end * 1000. - subs[-1].ms.end
        default_right_border = max(default_right_border, 0)

        progress_total = len(subs)

        fit_align = self.fit_align
        cur_audio = audio.AudioSegment.empty()
        tts_list = *(VOICER.voice(line.text) for line in
                     tqdm(subs, desc='TTSing', total=progress_total,
                          unit='line', dynamic_ncols=True)),
        for pos, tts in tqdm(enumerate(tts_list[:-1]),
                             desc='Fitting audio',
                             total=progress_total - 1, unit='line',
                             dynamic_ncols=True):
            ms = subs[pos].ms
            cur_audio += audio.fit(
                tts,
                ms.start - cur_audio.duration_ms,
                ms.duration,
                subs[pos + 1].ms.start - ms.end,
                fit_align
            )
        ms = subs[- 1].ms
        cur_audio += audio.fit(tts_list[-1],
                               ms.start - cur_audio.duration_ms,
                               ms.duration,
                               default_right_border,
                               fit_align)

        max_duration = ms.end
        audio_duration = cur_audio.duration_ms

        if audio_duration > max_duration:
            change_speed = audio_duration / max_duration
            rich.print(f'Changing audio speed to {change_speed:g}')
            cur_audio = audio.speed_change(cur_audio, change_speed)
        elif audio_duration != max_duration:
            cur_audio = audio.AudioSegment.silent(
                min(max_duration - audio_duration, subs[0].ms.start)
            ) + cur_audio

        result_dir = Path(target_sub).parent / '_result'
        result_dir.mkdir(exist_ok=True)
        result_out_audio = str(result_dir / f'{fn}_{self.language}.{self.audio_format}')

        if cleanup_audio is None:
            cleanup_audio = self.cleanup_level

        if target_vid:
            if self.ducking:
                audio.side_chain(audio.AudioSegment.from_file(target_vid),
                                 cur_audio,
                                 self.min_silence_len, self.silence_thresh, self.gain_during_overlay
                                 ).export(result_out_audio)
            else:
                audio.AudioSegment.from_file(target_vid).overlay(cur_audio,
                                                                 gain_during_overlay=self.gain_during_overlay
                                                                 ).export(result_out_audio)

            FFMpegWrapper.save_result_data(target_vid, result_out_audio, target_sub,
                                           result_dir / f'{fn}_{self.language}.mp4')
            if cleanup_audio:
                os.remove(result_out_audio)
        else:
            cur_audio.export(result_out_audio)
