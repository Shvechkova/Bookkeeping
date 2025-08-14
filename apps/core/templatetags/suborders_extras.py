from django import template
from decimal import Decimal

register = template.Library()


class SuborderAggregate:
    """Простой объект-обертка для возврата суммы и связанных полей.

    Имеет поля: amount, category_employee, month_bill
    """

    def __init__(self, amount, category_employee, month_bill=None):
        self.amount = amount
        self.category_employee = category_employee
        self.month_bill = month_bill


def _safe_amount(value):
    if value is None:
        return Decimal(0)
    try:
        return Decimal(value)
    except Exception:
        return Decimal(0)


@register.simple_tag
def get_suborder_for_name_month(suborders, suborder_name, month_id):
    """Возвращает SuborderAggregate: сумма по всем совпадениям; если совпадений нет — None.

    - Если найден один элемент — amount равен его сумме, category_employee/ month_bill берутся из него
    - Если найдено несколько — amount это сумма по всем элементам с тем же category_employee и month_bill
    """
    # Путь для QuerySet
    try:
        filtered = suborders.filter(
            category_employee__name=suborder_name, month_bill__id=month_id
        )
        first = filtered.first()
        if not first:
            return None
        total = sum((_safe_amount(item.amount) for item in filtered), Decimal(0))
        return SuborderAggregate(total, first.category_employee, first.month_bill)
    except Exception:
        # Путь для списка
        matched = []
        for item in suborders:
            try:
                if (
                    getattr(getattr(item, "category_employee", None), "name", None)
                    == suborder_name
                    and getattr(getattr(item, "month_bill", None), "id", None)
                    == month_id
                ):
                    matched.append(item)
            except Exception:
                continue
        if not matched:
            return None
        first = matched[0]
        total = sum((_safe_amount(it.amount) for it in matched), Decimal(0))
        return SuborderAggregate(total, first.category_employee, first.month_bill)


@register.simple_tag
def sum_by_employee_all_month(suborders, month_id):
    """Сумма всех SubcontractMonth.amount по сотрудникам (category_employee != None) за месяц.

    Работает и для QuerySet, и для списка.
    Возвращает Decimal сумму.
    """
    try:
        filtered = suborders.filter(
            category_employee__isnull=False, month_bill__id=month_id
        )
        return sum((_safe_amount(item.amount) for item in filtered), Decimal(0))
    except Exception:
        total = Decimal(0)
        for item in suborders:
            try:
                if (
                    getattr(getattr(item, "category_employee", None), "id", None)
                    is not None
                    and getattr(getattr(item, "month_bill", None), "id", None)
                    == month_id
                ):
                    total += _safe_amount(getattr(item, "amount", None))
            except Exception:
                continue
        return total


RU_MONTH_TO_NUM = {
    "Январь": 1,
    "Февраль": 2,
    "Март": 3,
    "Апрель": 4,
    "Май": 5,
    "Июнь": 6,
    "Июль": 7,
    "Август": 8,
    "Сентябрь": 9,
    "Октябрь": 10,
    "Ноябрь": 11,
    "Декабрь": 12,
}


@register.simple_tag
def sum_by_employee_all_group(suborders, month_name_ru, year_str):
    """Сумма по всем категориям сотрудников за группу (месяц+год по названию месяца и году строки)."""
    month_num = RU_MONTH_TO_NUM.get(str(month_name_ru))
    try:
        year_int = int(year_str)
    except Exception:
        year_int = None
    if not month_num or not year_int:
        return Decimal(0)
    try:
        filtered = suborders.filter(
            category_employee__isnull=False,
            month_bill__month__month=month_num,
            month_bill__month__year=year_int,
        )
        return sum((_safe_amount(item.amount) for item in filtered), Decimal(0))
    except Exception:
        total = Decimal(0)
        for item in suborders:
            try:
                month_field = getattr(getattr(item, "month_bill", None), "month", None)
                if (
                    getattr(getattr(item, "category_employee", None), "id", None)
                    is not None
                    and month_field is not None
                    and getattr(month_field, "month", None) == month_num
                    and getattr(month_field, "year", None) == year_int
                ):
                    total += _safe_amount(getattr(item, "amount", None))
            except Exception:
                continue
        return total


@register.simple_tag
def sum_by_employee_category_group(suborders, suborder_name, month_name_ru, year_str):
    """Сумма по конкретной категории сотрудников за группу (месяц+год)."""
    month_num = RU_MONTH_TO_NUM.get(str(month_name_ru))
    try:
        year_int = int(year_str)
    except Exception:
        year_int = None
    if not month_num or not year_int:
        return Decimal(0)
    try:
        filtered = suborders.filter(
            category_employee__name=suborder_name,
            month_bill__month__month=month_num,
            month_bill__month__year=year_int,
        )
        return sum((_safe_amount(item.amount) for item in filtered), Decimal(0))
    except Exception:
        total = Decimal(0)
        for item in suborders:
            try:
                month_field = getattr(getattr(item, "month_bill", None), "month", None)
                if (
                    getattr(getattr(item, "category_employee", None), "name", None)
                    == suborder_name
                    and month_field is not None
                    and getattr(month_field, "month", None) == month_num
                    and getattr(month_field, "year", None) == year_int
                ):
                    total += _safe_amount(getattr(item, "amount", None))
            except Exception:
                continue
        return total


