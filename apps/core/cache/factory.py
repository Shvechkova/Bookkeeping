# core/cache/factory.py
from django.core.cache import cache
from typing import Callable, Any
import hashlib

def create_subdomain(prefix: str, subdomain: str, timeout: int = 60 * 15):
    """
    Фабричная функция: создаёт класс-подраздел кэша.

    :param prefix: основной раздел (например, "storage")
    :param subdomain: подраздел (например, "servise")
    :param timeout: время жизни кэша в секундах
    :return: класс с методами .get() и .clear()
    """
    class Subdomain:

        @classmethod
        def _make_key(cls, *parts):
            """
            Генерирует ключ вида: cm:storage:servise:2025:4
            Если слишком длинный — хэширует.
            """
            key = f"cm:{cls.prefix}:{cls.subdomain}:{':'.join(map(str, parts))}"
            if len(key) > 200:
                h = hashlib.md5(key.encode()).hexdigest()
                return f"cm:{cls.prefix}:{cls.subdomain}:{h}"
            return key

        @classmethod
        def get(cls, calculate_func: Callable, version_keys, func_args=None, func_kwargs=None):
            """
            :param calculate_func: функция для кэширования
            :param version_keys: кортеж/список для генерации ключа (например, [year, bank_id])
            :param func_args: аргументы, которые передаются в функцию
            :param func_kwargs: именованные аргументы функции
            """
            func_args = func_args or ()
            func_kwargs = func_kwargs or {}

            # Генерируем ключ
            cache_key = cls._make_key(*version_keys)

            # Проверяем кэш
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

            # Выполняем функцию
            result = calculate_func(*func_args, **func_kwargs)
            cache.set(cache_key, result, timeout=cls.timeout)
            return result

        @classmethod
        def clear(cls, *parts):
            """
            Очищает кэш:
            - clear(2025, 4) → конкретный ключ
            - clear() → все ключи этого подраздела
            """
            if parts:
                cache.delete(cls._make_key(*parts))
            else:
                # Удаляем все ключи подраздела
                cache.delete_pattern(f"cm:{cls.prefix}:{cls.subdomain}:*")

    Subdomain.prefix = prefix
    Subdomain.subdomain = subdomain
    Subdomain.timeout = timeout
    
    
    return Subdomain