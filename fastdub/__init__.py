from __future__ import annotations

from multiprocessing import cpu_count

__all__ = ('PrettyViewPrefix', 'GlobalSettings')


class GlobalSettings:
    __slots__ = ()
    threads_count = cpu_count()
    export_video = True
    language = 'ru'
    watermark = ''


class PrettyViewPrefix:
    """Class for representing a number as units"""
    __slots__ = ()

    @staticmethod
    def from_any(size: float, div: float, base: str, prefixes) -> str:
        for prefix in prefixes[:-1]:
            if size < div:
                return f'{size:,g}{prefix}{base}'
            size /= div
        return f'{size:,g}{prefixes[-1]}{base}'

    @classmethod
    def from_bytes(cls, size: float) -> str:
        return cls.from_any(size, 1000., 'B', ('', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'))

    @classmethod
    def from_seconds(cls, size: float) -> str:
        return cls.from_any(size, 60., '', 'smh')
