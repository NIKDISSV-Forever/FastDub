from __future__ import annotations

import argparse

__all__ = ('PrettyViewPrefix',)

if not hasattr(argparse, 'BooleanOptionalAction'):
    class BooleanOptionalAction(argparse.Action):
        __slots__ = ()

        def __init__(self, option_strings, dest, default=None, type=None,
                     choices=None, required=False, help=None, metavar=None):
            _option_strings = ()
            for option_string in option_strings:
                _option_strings += option_string,
                if option_string.startswith('--'):
                    option_string = '--no-' + option_string[2:]
                    _option_strings += option_string,
            if help is not None and default is not None and default is not argparse.SUPPRESS:
                help += " (default: %(default)s)"
            super().__init__(option_strings=_option_strings, dest=dest, nargs=0, default=default, type=type,
                             choices=choices, required=required, help=help, metavar=metavar)

        def __call__(self, parser, namespace, values, option_string=None):
            if option_string in self.option_strings:
                setattr(namespace, self.dest, not option_string.startswith('--no-'))

        def format_usage(self):
            return ' | '.join(self.option_strings)


    argparse.BooleanOptionalAction = BooleanOptionalAction


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
