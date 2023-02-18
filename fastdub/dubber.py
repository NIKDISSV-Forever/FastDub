from __future__ import annotations

import os.path
import shutil
from pathlib import Path
from typing import Sequence

import rich.align
from tqdm import tqdm

from fastdub import audio, subtitles, voicer
from fastdub.audio import calc_speed_change_ffmpeg_arg
from fastdub.ffmpeg_wrapper import FFMpegWrapper

__all__ = ('Dubber', 'VOICER')

VOICER = voicer.Voicer()


class Dubber:
    __slots__ = (
        'fit_align', 'language', 'audio_format',
        'cleanup_audio', 'export_video',
        'ducking',
        'min_silence_len', 'silence_thresh', 'gain_during_overlay'
    )

    def __init__(self, voice: str, language: str, audio_format: str,
                 ducking: bool, min_silence_len: int, silence_thresh: float, gain_during_overlay: int,
                 fit_align: float = 2., cleanup_audio: bool = True, export_video: bool = True):
        self.language = language
        self.audio_format = audio_format
        self.fit_align = fit_align
        if voice:
            VOICER.set_voice(voice)

        self.ducking = ducking
        self.min_silence_len = min_silence_len
        self.silence_thresh = silence_thresh
        self.gain_during_overlay = gain_during_overlay

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

        rich.print(rich.align.Align(fn, 'center'))
        result_dir = Path(target_sub).parent / '_result'
        result_dir.mkdir(exist_ok=True)
        out_audio_base = result_dir / f'{fn}_{self.language}.{self.audio_format}'

        subs = subtitles.parse(target_sub)

        default_right_border = 0
        if target_vid and subs:
            default_right_border = FFMpegWrapper.get_video_duration_ms(target_vid) - subs[-1].ms.end
        default_right_border = max(default_right_border, 0)

        progress_total = len(subs)

        total_duration_ms = 0
        fit_align = self.fit_align
        audio_format = self.audio_format

        working_dir = result_dir / '_working_dir'
        working_dir.mkdir(exist_ok=True)

        _audio_filename_format = str(working_dir / ('{0:0>%i}.%s' % (len(str(progress_total)), audio_format))
                                     ).format
        filenames: tuple[str] = *(_audio_filename_format(pos) for pos in range(len(subs))),
        for pos, line in tqdm(enumerate(subs[:-1]),
                              desc='Creating audio',
                              total=progress_total - 1, unit='line',
                              dynamic_ncols=True):
            ms = subs[pos].ms
            tts = VOICER.voice(line.text)
            new_audio = audio.fit(
                tts,
                ms.start - total_duration_ms,
                ms.duration,
                subs[pos + 1].ms.start - ms.end,
                fit_align
            )
            total_duration_ms += new_audio.duration_ms
            new_audio.export(filenames[pos], audio_format)
        ms = subs[-1].ms
        tts = VOICER.voice(subs[-1].text)
        new_audio = audio.fit(tts,
                              ms.start - total_duration_ms,
                              ms.duration,
                              default_right_border,
                              fit_align)
        total_duration_ms += new_audio.duration_ms
        new_audio.export(filenames[-1], audio_format)

        with open(list_file := os.path.join(working_dir, 'list.txt'), 'w') as f:
            f.write('\n'.join(f"file '{fn}'" for fn in filenames))
        max_duration = ms.end

        ffmpeg_concat_args = ()
        if total_duration_ms > max_duration:
            change_speed = total_duration_ms / max_duration
            rich.print(f'Changing audio speed to {change_speed:g}')
            ffmpeg_concat_args += '-af', calc_speed_change_ffmpeg_arg(change_speed)
        else:
            ffmpeg_concat_args += '-c', 'copy'

        fitted_audio_file = str(out_audio_base.with_stem(f'_{out_audio_base.stem}'))
        rich.print('Concatenating parts...', flush=True)
        FFMpegWrapper.convert('-f', 'concat', '-safe', '0', '-i', list_file, *ffmpeg_concat_args,
                              fitted_audio_file)
        cur_audio = audio.AudioSegment.from_file(fitted_audio_file)
        shutil.rmtree(working_dir, ignore_errors=True)

        if total_duration_ms != max_duration:
            cur_audio = audio.AudioSegment.silent(
                min(max_duration - total_duration_ms, subs[0].ms.start)
            ) + cur_audio

        result_out_audio = str(out_audio_base)
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
            if export_video:
                FFMpegWrapper.save_result_data(target_vid, result_out_audio, target_sub,
                                               result_dir / f'{fn}_{self.language}.mp4')
                if cleanup_audio:
                    os.remove(result_out_audio)
        else:
            cur_audio.export(result_out_audio)
        os.remove(fitted_audio_file)
