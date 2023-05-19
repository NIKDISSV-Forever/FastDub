from __future__ import annotations

import math
import os.path
from copy import copy
from tempfile import TemporaryDirectory

import pydub.silence

from fastdub.ffmpeg_wrapper import FFMpegWrapper

__all__ = ('AudioSegment',
           'speed_change', 'calc_speed_change_ffmpeg_arg',
           'fit')


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
    if speed_changes <= 0:
        raise ValueError(f"Speed cannot be negative ({speed_changes}).\n"
                         "This is usually due to errors in subtitle timecodes.")
    if speed_changes == 1:
        return audio if allow_copy else copy(audio)
    with TemporaryDirectory() as tmp:
        inp = os.path.join(tmp, 'inp.wav')
        audio.export(inp)
        out = os.path.join(tmp, 'out.wav')
        FFMpegWrapper.convert('-i', inp,
                              '-af', calc_speed_change_ffmpeg_arg(speed_changes),
                              out, loglevel=log_level)
        return AudioSegment.from_file(out)


def calc_speed_change_ffmpeg_arg(speed_changes: float) -> str:
    """
    The given function takes in a float value representing the speed change
    and returns a corresponding FFMpeg argument string for changing the speed of an audio or video file.
    """
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
