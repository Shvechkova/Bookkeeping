# bank/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


from apps.bank.models import CategOperationsBetweenBank
from apps.core.cache.manager import cache_manager 
from apps.operation.models import Operation   # ← импортируем правильно   

# Список банков, которые нужно отслеживать
WATCHED_BANK_IDS = {4}  # например, только банк с id=4

def invalidate_storage_cache(instance, **kwargs):
    """
    Инвалидирует кэш storage.servise при изменении связанной модели.
    """
    # Определяем, с каким банком связан объект
    bank_ids = set()

    if hasattr(instance, 'bank_in') and instance.bank_in_id:
        bank_ids.add(instance.bank_in_id)
    if hasattr(instance, 'bank_to') and instance.bank_to_id:
        bank_ids.add(instance.bank_to_id)

    # Если объект не связан с нужными банками — выходим
    if not (bank_ids & WATCHED_BANK_IDS):
        return

    # Определяем год
    if hasattr(instance, 'data') and instance.data:
        year = instance.data.year
    else:
        # Если нет даты — можно сбросить все годы, или использовать текущий
        from datetime import datetime
        year = datetime.now().year

    # Инвалидируем кэш для всех watched банков и этого года
    for bank_id in bank_ids & WATCHED_BANK_IDS:
        cache_manager.storage.servise.clear(year, bank_id)
        # Если нужно — сбросить и другие подразделы
        # cache_manager.storage.bank.clear(year, bank_id)


# Подключаем сигналы
@receiver([post_save, post_delete], sender=Operation)
def on_operation_change(sender, instance, **kwargs):
    invalidate_storage_cache(instance, **kwargs)


@receiver([post_save, post_delete], sender=CategOperationsBetweenBank)
def on_category_change(sender, instance, **kwargs):
    # Если меняется категория, влияющая на "Забираем в хранилище"
    if instance.name in ["Забираем в наше хранилище", "откладываем в хранилище"]:
        # Нужно найти связанные операции
        ops = Operation.objects.filter(between_bank=instance)
        for op in ops:
            invalidate_storage_cache(op, **kwargs)