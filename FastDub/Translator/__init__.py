try:
    import translators
except ImportError:
    SUPPORTED = False
else:
    SUPPORTED = True
