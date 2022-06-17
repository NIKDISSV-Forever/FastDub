__all__ = 'SUPPORTED',
try:
    import translators
except ImportError:
    SUPPORTED = False
else:
    SUPPORTED = True
    __all__ += 'translators',
