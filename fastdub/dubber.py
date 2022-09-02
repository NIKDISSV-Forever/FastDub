from __future__ import annotations

import os.path
from contextlib import closing
from pprint import pp
from typing import Container

from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm

from fastdub import audio, subtitles, voicer
from fastdub.ffmpeg_wrapper import FFMpegWrapper

__all__ = ('Dubber', 'VOICER')

VOICER = voicer.Voicer()


class Dubber:
    __slots__ = (
        'fit_align', 'language',
        'ducking', 'min_silence_len', 'silence_thresh',
        'gain_during_overlay'
    )

    def __init__(self, voice: str, language: str, ducking: bool,
                 min_silence_len: int, silence_thresh: float, gain_during_overlay: int,
                 fit_align: float = 2.):
        self.language = language
        self.fit_align = fit_align
        if voice:
            VOICER.set_voice(voice)

        self.ducking = ducking
        self.min_silence_len = min_silence_len
        self.silence_thresh = silence_thresh
        self.gain_during_overlay = gain_during_overlay

    @staticmethod
    def collect_videos(path_to_files: str, skip_starts_underscore: bool = True,
                       exclude_files: Container[str] = None):
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
            self.dub_one(fn, exts[video_format], exts[subtitles_format])

    def dub_one(self, fn: str, target_mp4: str, target_srt: str, clean_up: int = 1):
        if target_mp4 is target_srt is None:
            return
        subs = subtitles.parse(target_srt)

        default_right_border = 0
        if target_mp4:
            video_clip: VideoFileClip
            with closing(VideoFileClip(target_mp4, audio=False)) as video_clip:
                default_right_border = video_clip.end * 1000. - subs[-1].ms.end
        default_right_border = max((default_right_border, 0))

        tqdm_total = len(subs)

        tts_list = [VOICER.voice(line.text) for line in
                    tqdm(subs, desc='TTSing', total=tqdm_total,
                         unit='line', dynamic_ncols=True, colour='white')]

        end_element_pos = tqdm_total - 1
        cur_audio = audio.AudioSegment.empty()

        for pos, tts, line in tqdm(
                ((i, tts, subs[i]) for i, tts in enumerate(tts_list)),
                desc='Fitting audio',
                total=tqdm_total, unit='line',
                dynamic_ncols=True, colour='white'):
            cur_audio += audio.fit(
                tts,
                line.ms.start - cur_audio.duration_ms,
                line.ms.duration,
                (default_right_border
                 if pos == end_element_pos else
                 (subs[
                      pos + 1].ms.start - line.ms.end)
                 ), self.fit_align
            )

        max_duration = subs[-1].ms.end
        audio_duration = cur_audio.duration_ms

        if audio_duration > max_duration:
            change_speed = audio_duration / max_duration
            print(f'Changing audio speed to {change_speed:g}')
            cur_audio = audio.speed_change(cur_audio, change_speed)
        elif audio_duration != max_duration:
            cur_audio = audio.AudioSegment.silent(
                min((max_duration - audio_duration, subs[0].ms.start))
            ) + cur_audio

        result_dir = os.path.join(os.path.dirname(target_srt), f'_{fn}_result')
        if not os.path.isdir(result_dir):
            os.mkdir(result_dir)

        target_out_audio = os.path.join(result_dir, f'_{self.language}.mp3')
        result_out_audio = os.path.join(result_dir, f'{self.language}.mp3')

        if target_mp4:
            with closing(VideoFileClip(target_mp4)) as video_clip:
                video_clip.audio.write_audiofile(target_out_audio)
                if self.ducking:
                    audio.side_chain(audio.AudioSegment.from_file(target_out_audio), cur_audio, self.min_silence_len,
                                     self.silence_thresh, self.gain_during_overlay
                                     ).export(result_out_audio)
                else:
                    audio.AudioSegment.from_file(target_out_audio).overlay(cur_audio,
                                                                           gain_during_overlay=self.gain_during_overlay
                                                                           ).export(result_out_audio)

            FFMpegWrapper.save_result_data(target_mp4, result_out_audio, target_srt,
                                           os.path.join(result_dir, f'{self.language}.mp4'))
            if clean_up > 0:
                os.remove(target_out_audio)
                if clean_up > 1:
                    os.remove(result_out_audio)
                    if clean_up > 2:
                        VOICER.cleanup()
        else:
            cur_audio.export(result_out_audio)
