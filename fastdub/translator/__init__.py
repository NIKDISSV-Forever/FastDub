from __future__ import annotations

from typing import Callable

__all__ = ('SUPPORTED',)

try:
    from translators import server
    from fastdub.translator import subs_translate

    SERVICES = *server.tss.translators_dict.keys(),


    def get_service_by_name(service: str) -> Callable:
        return server.tss.translators_dict[service]
except ImportError:
    SUPPORTED = False
else:
    SUPPORTED = True
    __all__ += ('translators', 'SERVICES', 'get_service_by_name', 'subs_translate')
