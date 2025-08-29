# core/cache/manager.py
from .factory import create_subdomain
from .config import CACHE_SECTIONS

class CacheManager:
    """
    Автоматически построенный менеджер кэша.
    Примеры:
        cache_manager.storage.servise.get(...)
        cache_manager.analytics.monthly.clear(2025)
    """

    def __init__(self):
        self._build_sections()

    def _build_sections(self):
        """
        Динамически создаёт разделы и подразделы на основе CACHE_SECTIONS.
        """
        for section_name, subdomains in CACHE_SECTIONS.items():
            # Создаём класс-раздел (например, Storage)
            section_class = type(section_name.capitalize(), (), {})

            for sub_name, options in subdomains.items():
                timeout = options.get("timeout", 60 * 15)
                # Создаём подраздел через фабрику
                subdomain_class = create_subdomain(
                    prefix=section_name,
                    subdomain=sub_name,
                    timeout=timeout
                )
                # Добавляем как атрибут
                setattr(section_class, sub_name, subdomain_class)

            # Добавляем раздел в менеджер
            setattr(self, section_name, section_class())


# Создаём глобальный экземпляр
cache_manager = CacheManager()