import os.path
from contextlib import closing
from typing import Container

from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm

from FastDub import SrtSubtitles, Voicer, Audio

__all__ = ('Dubber',)

from FastDub.FFMpeg import FFMpegWrapper


class Dubber:
    __slots__ = ('DUCKING_ARGS', 'VIDEO_FORMAT', 'SUBTITLES_FORMAT', 'fit_align')

    VOISER = Voicer.Voicer()

    def __init__(self, voice: str, ducking: bool,
                 min_silence_len: int, silence_thresh: float, gain_during_overlay: int,
                 video_format: str = '.mp4', subtitles_format: str = '.srt', fit_align: float = 1.):

        self.VIDEO_FORMAT = video_format if video_format.startswith('.') else f'.{video_format}'
        self.SUBTITLES_FORMAT = subtitles_format if subtitles_format.startswith('.') else f'.{subtitles_format}'
        self.fit_align = fit_align
        if voice:
            self.VOISER.set_voice(voice)
        self.DUCKING_ARGS = (min_silence_len, silence_thresh, gain_during_overlay) if ducking else None

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
        subtitles = SrtSubtitles.parse(target_srt)
        end_element_pos = len(subtitles) - 1

        if target_mp4:
            video_clip: VideoFileClip
            with closing(VideoFileClip(target_mp4, audio=False)) as video_clip:
                default_right_border = video_clip.end * 1000. - subtitles[-1].ms.end
        audio = Audio.AudioSegment.empty()

        current_line: SrtSubtitles.Line
        _pb = tqdm(enumerate(subtitles), total=end_element_pos + 1, unit='line',
                   dynamic_ncols=True, colour='white')
        for pos, current_line in _pb:
            _pb.desc = f'{fn} - {current_line.ms}'
            audio += Audio.fit(
                self.VOISER.voice(current_line.text), current_line.ms.start - audio.duration_ms,
                current_line.ms.duration,
                (default_right_border
                 if pos == end_element_pos else
                 (subtitles[pos + 1].ms.start - current_line.ms.end)
                 ), self.fit_align)
        max_duration = subtitles[-1].ms.end
        if (audio_duration := audio.duration_ms) > max_duration:
            change_speed = audio_duration / max_duration
            print(f'Changing audio speed to {round(change_speed, 3)}')
            audio = Audio.speed_change(audio, change_speed)
        elif audio_duration != max_duration:
            audio = Audio.AudioSegment.silent(max_duration - audio_duration) + audio
        result_dir = os.path.join(os.path.dirname(target_srt), f'_{fn}_result')
        if not os.path.isdir(result_dir):
            os.mkdir(result_dir)

        target_out_audio = os.path.join(result_dir, 'video.mp3')
        result_out_audio = os.path.join(result_dir, 'result.mp3')
        result_out_video = os.path.join(result_dir, 'result.mp4')

        if target_mp4:
            with closing(VideoFileClip(target_mp4)) as video_clip:
                video_clip.audio.write_audiofile(target_out_audio)
                if self.DUCKING_ARGS:
                    Audio.duck(Audio.AudioSegment.from_file(target_out_audio), audio, *self.DUCKING_ARGS
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
