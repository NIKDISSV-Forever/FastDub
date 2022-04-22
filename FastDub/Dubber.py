from __future__ import annotations

import os.path
from contextlib import closing
from typing import Container

from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm

from FastDub import Subtitles, Voicer, Audio

__all__ = ('Dubber',)

from FastDub.FFMpeg import FFMpegWrapper


class Dubber:
    __slots__ = (
        'VIDEO_FORMAT', 'SUBTITLES_FORMAT',
        'fit_align',
        'ducking', 'min_silence_len', 'silence_thresh',
        'gain_during_overlay'
    )

    VOISER = Voicer.Voicer()

    def __init__(self, voice: str, ducking: bool,
                 min_silence_len: int, silence_thresh: float, gain_during_overlay: int,
                 video_format: str = '.mp4', subtitles_format: str = '.srt', fit_align: float = 1.):

        self.VIDEO_FORMAT = video_format if video_format.startswith('.') else f'.{video_format}'
        self.SUBTITLES_FORMAT = subtitles_format if subtitles_format.startswith('.') else f'.{subtitles_format}'
        self.fit_align = fit_align
        if voice:
            self.VOISER.set_voice(voice)

        self.ducking = ducking
        self.min_silence_len = min_silence_len
        self.silence_thresh = silence_thresh
        self.gain_during_overlay = gain_during_overlay

    def dub_dir(self, path_to_files: str, skip_starts_underscore: bool = True,
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
            else:
                videos[filename] = {ext: os.path.join(path_to_files, file)}
        for fn, exts in videos.items():
            self.dub_one(fn, exts.get(self.VIDEO_FORMAT), exts.get(self.SUBTITLES_FORMAT))

    def dub_one(self, fn: str, target_mp4: str, target_srt: str, clean_up: int = 1):
        subtitles = Subtitles.parse(target_srt)

        if target_mp4:
            video_clip: VideoFileClip
            with closing(VideoFileClip(target_mp4, audio=False)) as video_clip:
                default_right_border = video_clip.end * 1000. - subtitles[-1].ms.end

        tqdm_total = len(subtitles)

        tts_list = [self.VOISER.voice(line.text) for line in
                    tqdm(subtitles, desc='TTSing', total=tqdm_total, unit='line',
                         dynamic_ncols=True, colour='white')]

        end_element_pos = tqdm_total - 1

        fits = []
        total_dubbed = 0
        for pos, tts, line in tqdm(
                [(i, tts, subtitles[i]) for i, tts in enumerate(tts_list)],
                desc='Fitting Audio',
                total=tqdm_total, unit='line',
                dynamic_ncols=True, colour='white'):
            one_fit = Audio.fit(
                tts,
                line.ms.start - total_dubbed,
                line.ms.duration,
                (default_right_border
                 if pos == end_element_pos else
                 (subtitles[
                      pos + 1].ms.start - line.ms.end)
                 ), self.fit_align)
            total_dubbed += one_fit.duration_ms
            fits.append(one_fit)

        audio = Audio.AudioSegment.empty()
        for fit in tqdm(fits, desc='Bonding Audio', total=tqdm_total, unit='segment',
                        dynamic_ncols=True, colour='white'):
            audio += fit

        max_duration = subtitles[-1].ms.end
        audio_duration = audio.duration_ms

        if audio_duration > max_duration:
            change_speed = audio_duration / max_duration
            print(f'Changing audio speed to {round(change_speed, 3)}')
            audio = Audio.speed_change(audio, change_speed)
        elif audio_duration != max_duration:
            audio = Audio.AudioSegment.silent(
                min((max_duration - audio_duration, subtitles[0].ms.start))
            ) + audio

        result_dir = os.path.join(os.path.dirname(target_srt), f'_{fn}_result')
        if not os.path.isdir(result_dir):
            os.mkdir(result_dir)

        target_out_audio = os.path.join(result_dir, 'video.mp3')
        result_out_audio = os.path.join(result_dir, 'result.mp3')
        result_out_video = os.path.join(result_dir, 'result.mp4')

        if target_mp4:
            with closing(VideoFileClip(target_mp4)) as video_clip:
                video_clip.audio.write_audiofile(target_out_audio)
                if self.ducking:
                    Audio.side_chain(Audio.AudioSegment.from_file(target_out_audio), audio, self.min_silence_len,
                                     self.silence_thresh, self.gain_during_overlay
                                     ).export(result_out_audio)
                else:
                    Audio.AudioSegment.from_file(target_out_audio).overlay(audio, self.gain_during_overlay
                                                                           ).export(result_out_audio)

            FFMpegWrapper.replace_audio_in_video(target_mp4, result_out_audio, result_out_video)
            if clean_up > 0:
                os.remove(target_out_audio)
                if clean_up > 1:
                    os.remove(result_out_audio)
                    if clean_up > 2:
                        self.VOISER.cleanup()
        else:
            audio.export(result_out_audio)
