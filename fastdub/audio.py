from __future__ import annotations

import math
import os.path
from copy import copy
from math import inf
from tempfile import TemporaryDirectory

import pydub.silence
from tqdm import tqdm

from fastdub.ffmpeg_wrapper import FFMpegWrapper

__all__ = ('AudioSegment',
           'speed_change', 'calc_speed_change_ffmpeg_arg',
           'fit', 'side_chain')


class AudioSegment(pydub.AudioSegment):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration_ms = self.duration_seconds * 1000.

    def append(self, seg, _=None):
        """pydub.AudioSegment. Without cross-fade."""
        seg1, seg2 = AudioSegment._sync(self, seg)
        # noinspection PyProtectedMember
        return seg1._spawn(seg1._data + seg2._data)

    __add__ = append


def speed_change(audio: AudioSegment, speed_changes: float, allow_copy: bool = True, log_level: str = 'error'
                 ) -> AudioSegment:
    if speed_changes == 1.:
        return audio if allow_copy else copy(audio)
    if speed_changes <= 0.:
        raise ValueError(f"Speed cannot be negative ({speed_changes}).\n"
                         "This is usually due to errors in subtitle timecodes.")

    with TemporaryDirectory() as tmp:
        inp = os.path.join(tmp, 'inp.mp3')
        audio.export(inp)
        out = os.path.join(tmp, 'out.mp3')
        FFMpegWrapper.convert('-i', inp,
                              '-af', calc_speed_change_ffmpeg_arg(speed_changes),
                              out, loglevel=log_level)
        return AudioSegment.from_file(out)


def calc_speed_change_ffmpeg_arg(speed_changes: float) -> str:
    if .5 <= speed_changes <= 100.:
        return f'atempo={speed_changes}'
    if .25 <= speed_changes <= 10_000.:
        return f'atempo=sqrt({speed_changes}),atempo=sqrt({speed_changes})'
    power = math.ceil(math.log(speed_changes, .5 if speed_changes < .5 else 100.))
    return (f'atempo={speed_changes}^(1/{power}),' * power)[:-1]


def fit(audio: AudioSegment,
        left_border: float, need_duration: float, right_border: float,
        align: float) -> AudioSegment:
    """Fits audio to the borders of the subtitles."""
    if (audio_duration := audio.duration_ms) > (free := (left_border + need_duration + right_border)):
        audio = speed_change(audio, audio_duration / free)
        audio_duration = audio.duration_ms
    return AudioSegment.silent(
        (free - audio_duration) / align
        if audio_duration > need_duration + right_border
        else left_border) + audio


def side_chain(sound1: AudioSegment, sound2: AudioSegment,
               min_silence_len: int = 100, silence_thresh: float = -inf,
               gain_during_overlay: int = -10
               ) -> AudioSegment:
    for start, end in tqdm(
            pydub.silence.detect_nonsilent(sound2, min_silence_len=min_silence_len, silence_thresh=silence_thresh),
            desc="Ducking"):
        sound1 = sound1.overlay(sound2[start:end], start, times=1, gain_during_overlay=gain_during_overlay)
    return sound1
