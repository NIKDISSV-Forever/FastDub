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


def _no_update_voice_anchor(_):
    return False


class Voicer:
    __slots__ = ('engine', 'cache_dir', '_update_voice_anchor', '_nul_file')

    def __init__(self, cache_dir: str = None, anchor: str = '!:', tts_driver_name: str = None, tts_debug: bool = False):
        if anchor:
            def _update_voice_anchor(line: str) -> bool:
                if line.startswith(anchor):
                    self.set_voice(line.removeprefix(anchor))
                    return True
                return False
        else:
            _update_voice_anchor = _no_update_voice_anchor
        self._update_voice_anchor = _update_voice_anchor

        cache_dir = Path(__file__).parent / '_cached_texts' if cache_dir is None else Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        nul_file = cache_dir / 'nul.wav'
        if not nul_file.is_file():
            AudioSegment.silent(0).export(nul_file, 'wav')
        self.cache_dir = cache_dir
        self._nul_file = str(nul_file)

        self.engine = pyttsx3.init(tts_driver_name, tts_debug)

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

    def voice(self, text: str) -> str:
        text = text.strip()
        if not text:
            return self._nul_file

        if self._update_voice_anchor((lines := text.splitlines())[0]):
            text = '\n'.join(lines[1:])

        cached_file = f'''{self.cache_dir / md5(f"{text}{self.engine.proxy.getProperty('voice')}".encode())
        .hexdigest()}.wav'''
        if not isfile(cached_file):
            self.engine.save_to_file(text, cached_file, 'fastdub')
            self.engine.runAndWait()
        return cached_file
