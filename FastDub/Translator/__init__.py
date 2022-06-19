__all__ = 'SUPPORTED',
try:
    import translators

    SERVICES = [i[1:] for i in dir(translators.apis) if i.startswith('_') and not i.startswith('__')]


    def get_service_by_name(service: str):
        return getattr(translators, service)
except ImportError:
    SUPPORTED = False
else:
    SUPPORTED = True
    __all__ += 'translators', 'SERVICES', 'get_service_by_name'
