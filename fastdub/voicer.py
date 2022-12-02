from __future__ import annotations

from hashlib import md5
from os.path import isfile
from pathlib import Path
from shutil import rmtree

import pyttsx3

from fastdub.audio import AudioSegment

__all__ = ('UnknownVoice', 'VOICES_NAMES', 'VOICES_ID', 'Voicer')


class UnknownVoice(Exception):
    __slots__ = ()


_voices = pyttsx3.init().proxy.getProperty('voices')
VOICES_NAMES = {i.name.casefold(): i for i in _voices}
VOICES_ID = {i.id: i for i in _voices}
del _voices


class Voicer:
    __slots__ = ('engine', 'cache_dir', '_update_voice_anchor')

    def __init__(self, cache_dir: str = None, anchor: str = '!:'):
        if anchor:
            def _update_voice_anchor(line: str) -> bool:
                if line.startswith(anchor):
                    self.set_voice(line.removeprefix(anchor))
                    return True
                return False
        else:
            def _update_voice_anchor(_: str) -> bool:
                return False
        self._update_voice_anchor = _update_voice_anchor
        self.cache_dir = Path(__file__).parent / '_cached_texts' if cache_dir is None else Path(cache_dir)
        self.engine = pyttsx3.init()
        if not self.cache_dir.is_dir():
            self.cache_dir.mkdir(parents=True)

    def cleanup(self):
        rmtree(self.cache_dir)

    def set_voice(self, voice: str):
        voice_name = voice.casefold()
        voice_property = self.engine.proxy.getProperty('voice')
        voice = VOICES_NAMES.get(voice_name)
        if not voice:
            raise UnknownVoice(f'{voice_name} not in {str(tuple(VOICES_NAMES.keys()))}')
        if VOICES_ID.get(voice_property).name.casefold() != voice_name:
            self.engine.proxy.setProperty('voice', voice.id)

    def voice(self, text: str) -> AudioSegment:
        text = text.strip()
        if not text:
            return AudioSegment.silent(0)

        if self._update_voice_anchor((lines := text.splitlines())[0]):
            text = '\n'.join(lines[1:])

        cached = f'''{self.cache_dir / md5(f"{text}{self.engine.proxy.getProperty('voice')}".encode())
        .hexdigest()}.wav'''
        if not isfile(cached):
            self.engine.proxy.save_to_file(text, cached, None)
            self.engine.runAndWait()
        return AudioSegment.from_file(cached, format='wav')
