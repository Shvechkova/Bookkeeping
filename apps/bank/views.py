import datetime
import logging
from django.db.models.functions import ExtractMonth
from apps.core.utils import (
    create_month_categ_persent,
    fill_operations_arrays_ip,
    fill_operations_arrays_ooo,
    get_id_categ_oper,
)
import pymorphy3
import itertools
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.db.models.functions import TruncMonth
from django.db.models import Prefetch, OuterRef
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q, F, OrderBy, Case, When, Value
from django.db import models
from apps.bank.models import (
    CATEGORY_OPERACCOUNT,
    Bank,
    CategForPercentGroupBank,
    CategNalog,
    CategOperationsBetweenBank,
    CategPercentGroupBank,
    GroupeOperaccount,
    GroupeSalary,
)
from apps.employee.models import Employee
from apps.operation.models import Operation
from apps.service.models import Service, SubcontractOtherCategory
from project.settings import MONTHS_RU
import locale
import copy
from django.core.cache import cache


# Внутренние счета
def inside(request):
    title = "Внутренние счета"
    type_url = "inside"
    context = {
        "title": title,
        "type_url": type_url,
    }

    return render(request, "bank/inside/inside_all.html", context)


def oper_accaunt(request):

    locale.setlocale(locale.LC_ALL, "")
    title = "oper_accaunt"
    type_url = "inside"
    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month
    # куки для сортировки
    if (
        request.COOKIES.get("sortOperAccount")
        and request.COOKIES.get("sortOperAccount") != "0"
    ):
        bank_id = request.COOKIES["sortOperAccount"]
        bank_id = [int(bank_id)]
    else:
        bank_id = [1, 2, 3]

    # Получаем операции
    operations = (
        Operation.objects.filter(
            operaccount__isnull=False, data__year__gte=year_now, bank_in__in=bank_id
        )
        .select_related("operaccount")
        .prefetch_related()
        .order_by("-data")
    )
    operations_old = (
        Operation.objects.filter(
            operaccount__isnull=False, data__year__lt=year_now, bank_in__in=bank_id
        )
        .select_related("operaccount")
        .prefetch_related()
        .order_by("-data")
    )

    category = CATEGORY_OPERACCOUNT
    groupeis = GroupeOperaccount.objects.all()

    # Создаем морфологический анализатор
    morph = pymorphy3.MorphAnalyzer(lang="ru")

    # Создаем структуру для хранения данных по категориям и счетам
    operations_by_category = {}
    for cat in CATEGORY_OPERACCOUNT:
        cat_id = cat[0]
        operations_by_category[cat_id] = {
            "name": cat[1],  # Название категории
            "accounts": {},  # Словарь для счетов
        }

    # Получаем все счета одним запросом
    all_accounts = GroupeOperaccount.objects.all()

    # Создаем список месяцев текущего года
    months_current_year = []
    for month in range(1, month_now + 1):
        month_name = MONTHS_RU[month - 1]
        months_current_year.append(month_name)
    months_current_year.reverse()

    # Группируем счета по категориям в памяти
    accounts_by_category = {}
    for account in all_accounts:
        if account.category not in accounts_by_category:
            accounts_by_category[account.category] = []
        accounts_by_category[account.category].append(account)

    # Инициализируем структуру данных для всех категорий, счетов и месяцев
    for cat_id, cat_data in operations_by_category.items():
        # Получаем все счета для данной категории
        accounts = accounts_by_category.get(cat_id, [])
        for account in accounts:
            cat_data["accounts"][account.name] = {
                "account": account,
                "account_id": account.id,
                "months": {},
            }
            # Инициализируем месяцы для каждого счета
            for month in months_current_year:
                cat_data["accounts"][account.name]["months"][month] = {
                    "operations": [],
                    "total": 0,
                    "comment": False,
                }

    # Группируем операции
    for operation in operations:

        month_name = morph.parse(operation.data.strftime("%B"))[0].normal_form.title()

        account = operation.operaccount
        category_id = account.category
        comment = operation.comment

        if category_id in operations_by_category:
            account_name = account.name
            if account_name in operations_by_category[category_id]["accounts"]:
                if (
                    month_name
                    in operations_by_category[category_id]["accounts"][account_name][
                        "months"
                    ]
                ):
                    # Добавляем операцию
                    operations_by_category[category_id]["accounts"][account_name][
                        "months"
                    ][month_name]["operations"].append(operation)
                    if comment:

                        operations_by_category[category_id]["accounts"][account_name][
                            "months"
                        ][month_name]["comment"] = True
                    operations_by_category[category_id]["accounts"][account_name][
                        "months"
                    ][month_name]["total"] += operation.amount
    # Преобразуем в список для шаблона
    operations_arr = []
    for cat_id, cat_data in operations_by_category.items():
        category_info = {
            "category_id": cat_id,
            "category_name": cat_data["name"],
            "accounts": [],
        }

        # Добавляем данные по счетам
        for account_name, account_data in cat_data["accounts"].items():
            account_info = {
                "name": account_name,
                "account": account_data["account"],
                "account_id": account_data["account_id"],
                "months": [],
            }

            # Добавляем данные по месяцам
            for i, month_name in enumerate(months_current_year):
                month_data = account_data["months"][month_name]
                month_info = {
                    "month": month_name,
                    "month_number": len(months_current_year) - i,
                    "date_start": datetime.datetime(
                        year_now, len(months_current_year) - i, 1
                    ),  # Первое число месяца и год в обратном порядке
                    "operations": month_data["operations"],
                    "total": month_data["total"],
                    "budget": 0,  # Инициализируем бюджет
                    "comment": month_data["comment"],
                }
                if i < len(months_current_year) - 1:
                    prev_month = months_current_year[i + 1]
                    prev_month_total = account_data["months"][prev_month]["total"]
                    month_info["budget"] = prev_month_total

                account_info["months"].append(month_info)

            category_info["accounts"].append(account_info)

        operations_arr.append(category_info)

    for category_info in operations_arr:
        totals_by_month = []
        for i, month_name in enumerate(months_current_year):
            total = 0
            for account in category_info["accounts"]:
                total += account["months"][i]["total"]
            totals_by_month.append(total)
        category_info["totals_by_month"] = totals_by_month

    # Группируем старые операции по годам
    operations_old_by_year = {}
    for operation in operations_old:
        comment = operation.comment
        year = operation.data.year
        if year not in operations_old_by_year:
            operations_old_by_year[year] = {
                "year": year,
                "categories": {},
                "total_year": 0,
            }

            # Инициализируем структуру для категорий
            for cat in CATEGORY_OPERACCOUNT:
                cat_id = cat[0]
                operations_old_by_year[year]["categories"][cat_id] = {
                    "name": cat[1],
                    "accounts": {},
                    "total_category": 0,
                }

                # Получаем счета для данной категории
                accounts = accounts_by_category.get(cat_id, [])
                for account in accounts:
                    operations_old_by_year[year]["categories"][cat_id]["accounts"][
                        account.name
                    ] = {
                        "account": account,
                        "account_id": account.id,
                        "months": {},
                        "total_account": 0,
                    }

                    # Инициализируем месяцы в прямом порядке
                    for month in range(1, 13):
                        month_name = MONTHS_RU[month - 1]
                        operations_old_by_year[year]["categories"][cat_id]["accounts"][
                            account.name
                        ]["months"][month_name] = {
                            "operations": [],
                            "total": 0,
                            "comment": False,
                        }

        # Добавляем операцию в соответствующую структуру
        month_name = morph.parse(operation.data.strftime("%B"))[0].normal_form.title()
        account = operation.operaccount
        category_id = account.category
        account_name = account.name

        if category_id in operations_old_by_year[year]["categories"]:
            if (
                account_name
                in operations_old_by_year[year]["categories"][category_id]["accounts"]
            ):
                month_data = operations_old_by_year[year]["categories"][category_id][
                    "accounts"
                ][account_name]["months"][month_name]
                month_data["operations"].append(operation)
                month_data["total"] += operation.amount

                # Обновляем суммы
                operations_old_by_year[year]["categories"][category_id]["accounts"][
                    account_name
                ]["total_account"] += operation.amount
                operations_old_by_year[year]["categories"][category_id][
                    "total_category"
                ] += operation.amount
                operations_old_by_year[year]["total_year"] += operation.amount
                if comment:

                    operations_old_by_year[year]["categories"][category_id]["accounts"][
                        account_name
                    ]["months"][month_name]
                month_data["comment"] = True

    # # Преобразуем в список для шаблона
    operations_old_arr = []
    for year in sorted(operations_old_by_year.keys(), reverse=True):
        year_data = operations_old_by_year[year]
        year_info = {
            "year": year,
            "total_year": year_data["total_year"],
            "categories": [],
            "totals_by_month": [0]
            * 12,  # Инициализируем массив для итогов по месяцам за год
        }

        for cat_id, cat_data in year_data["categories"].items():
            category_info = {
                "category_id": cat_id,
                "category_name": cat_data["name"],
                "total_category": cat_data["total_category"],
                "accounts": [],
                "totals_by_month": [0]
                * 12,  # Инициализируем массив для итогов по месяцам
            }

            for account_name, account_data in cat_data["accounts"].items():
                account_info = {
                    "name": account_name,
                    "account": account_data["account"],
                    "account_id": account_data["account_id"],
                    "total_account": account_data["total_account"],
                    "months": [],
                }

                # Добавляем месяцы в прямом порядке
                for month in range(1, 13):
                    month_name = MONTHS_RU[month - 1]
                    month_data = account_data["months"][month_name]
                    month_info = {
                        "month": month_name,
                        "month_number": month,
                        "date_start": datetime.datetime(year, month, 1),
                        "operations": month_data["operations"],
                        "total": month_data["total"],
                        "comment": month_data["comment"],
                    }
                    account_info["months"].append(month_info)
                    # Добавляем сумму в общий итог по месяцу для категории
                    category_info["totals_by_month"][month - 1] += month_data["total"]
                    # Добавляем сумму в общий итог по месяцу для года
                    year_info["totals_by_month"][month - 1] += month_data["total"]

                category_info["accounts"].append(account_info)

            year_info["categories"].append(category_info)

        operations_old_arr.append(year_info)

    context = {
        "title": title,
        "type_url": type_url,
        "operations": operations_arr,
        "operations_old": operations_old_arr,
        "groupeis": groupeis,
        "category": category,
        "months": months_current_year,
        "all_months": MONTHS_RU,
        "data": data,
        "year_now": str(year_now),
    }

    return render(request, "bank/inside/inside_one_oper_accaunt.html", context)


def salary(request):
    import locale

    locale.setlocale(locale.LC_ALL, "")

    title = "salary"
    type_url = "inside"

    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    year_now_st = str(year_now)
    month_now = datetime.datetime.now().month
    date_start_year = str(year_now) + "-01-01"

    month_now_name = MONTHS_RU[month_now - 1]
    # куки для установки дат сортировки
    q_object = Q()

    if request.COOKIES.get("sortSalary"):
        active = request.COOKIES["sortSalary"]
        if active == "1":
            q_object &= Q(date_end__isnull=True)
            q_object |= Q(date_end__year=year_now_st)
        else:
            q_object &= Q(date_end__year__lte=year_now_st)
    else:
        q_object &= Q(date_end__isnull=True)
        q_object |= Q(date_end__year=year_now_st)

    # Получаем активных сотрудников
    employee_now_year = Employee.objects.filter(q_object)

    # Создаем морфологический анализатор
    morph = pymorphy3.MorphAnalyzer(lang="ru")

    # Создаем список месяцев текущего года в обратном порядке
    months_current_year = []
    for month in range(1, month_now + 1):
        month_name = MONTHS_RU[month - 1]
        months_current_year.append(month_name)

    month_leng_total_month = len(months_current_year)
    months_current_year.reverse()
    months_current_year_2 = months_current_year.copy()
    all_categories_qs = (
        GroupeSalary.objects.all()
        .select_related("bank")
        .prefetch_related(Prefetch("bank"))
    )
    all_categories_bank = all_categories_qs.values_list("bank", "name", "id")

    cat_name_id = {}
    for cat in all_categories_qs:
        cat_name_id[cat.name] = cat.id
    # Определяем группы категорий
    salary_groups = {
        "group1": ["Оф ЗП (10 число)", "Оф Аванс", "Отпуск", "Оф Премия", "Больничный"],
        "group2": ["ЗП $", "Премия $", "Отпуск $"],
        "group3": ["КВ $", "КВ ИП", "квартальная премия"],
        "group4": ["Выдано в долг", "Возврат долга"],
    }
    salary_groups_bank = {}

    # Получаем операции
    operations = (
        Operation.objects.filter(
            salary__isnull=False,
            data__year__gte=year_now,
        )
        .select_related("salary")
        .prefetch_related()
        .order_by("-data")
    )

    operations_old = (
        Operation.objects.filter(
            salary__isnull=False,
            data__year__lt=year_now,
        )
        .select_related("salary", "employee")
        .prefetch_related()
        .order_by("-data")
    )

    # Структура для хранения данных
    employees_data = {}

    # Инициализируем структуру данных для каждого сотрудника
    for employee in employee_now_year:
        employees_data[employee.id] = {
            "employee": employee,
            "months": {},
            "groups": {
                "group1": {"total": 0, "categories": {}},
                "group2": {"total": 0, "categories": {}},
                "group3": {"total": 0, "categories": {}},
                "group4": {"total": 0, "categories": {}},
            },
        }

        # Инициализируем месяцы
        for month in months_current_year:
            employees_data[employee.id]["months"][month] = {
                "operations": [],
                "group1_total": 0,
                "group2_total": 0,
                "group3_total": 0,
                "group4_total": 0,
            }

    for dk in all_categories_qs:
        salary_groups_bank[dk.name] = dk.bank.id

    # Обрабатываем операции
    for operation in operations:
        employee_id = operation.employee.id
        if employee_id not in employees_data:
            continue

        month_name = morph.parse(operation.data.strftime("%B"))[0].normal_form.title()
        if month_name not in months_current_year:
            continue

        # Получаем название категории
        category = operation.salary.name
        amount = operation.amount

        # Определяем группу категории
        group = None
        for group_name, categories in salary_groups.items():
            if category in categories:
                group = group_name
                break

        if group:
            # Добавляем операцию в соответствующий месяц
            employees_data[employee_id]["months"][month_name]["operations"].append(
                operation
            )

            # Обновляем итоги по группам
            if group == "group1":
                if category == "Оф ЗП (10 число)":
                    # Для Оф ЗП (10 число) добавляем в итог предыдущего месяца (в обратном списке)
                    current_index = months_current_year.index(month_name)
                    prev_month_index_categ = current_index + 1
                    if prev_month_index_categ < len(months_current_year):
                        prev_month_categ = months_current_year[prev_month_index_categ]
                        employees_data[employee_id]["months"][prev_month_categ][
                            "group1_total"
                        ] += amount
                else:
                    employees_data[employee_id]["months"][month_name][
                        "group1_total"
                    ] += amount
            else:
                employees_data[employee_id]["months"][month_name][
                    f"{group}_total"
                ] += amount

            # Обновляем общие итоги по группам
            if group == "group4":
                # Для группы 4 (долги) считаем остаток
                employees_data[employee_id]["groups"][group]["total"] += amount
            else:
                employees_data[employee_id]["groups"][group]["total"] += amount

            # Добавляем категорию в группу
            if (
                category
                not in employees_data[employee_id]["groups"][group]["categories"]
            ):
                employees_data[employee_id]["groups"][group]["categories"][category] = 0
            employees_data[employee_id]["groups"][group]["categories"][
                category
            ] += amount

    # Обрабатываем старые операции
    operations_old_by_year = {}

    # Сначала получаем все уникальные годы из операций
    years_with_operations = set(operation.data.year for operation in operations_old)

    # Создаем структуру только для годов с операциями
    for year in sorted(years_with_operations, reverse=True):
        operations_old_by_year[year] = {
            "year": year,
            "employees": {},
        }
        # Инициализируем структуру для всех текущих сотрудников
        for employee in employee_now_year:
            operations_old_by_year[year]["employees"][employee.id] = {
                "employee": employee,
                "categories_by_month": {},
                "operations_by_month": {},
                "total_by_month": [0] * len(MONTHS_RU),
                "groups_full": [],
            }

    # Заполняем данные операциями
    for operation in operations_old:
        year = operation.data.year
        if year not in operations_old_by_year:
            continue

        employee_id = operation.employee.id
        if employee_id not in operations_old_by_year[year]["employees"]:
            continue

        # Добавляем операцию в соответствующий месяц
        month_name = morph.parse(operation.data.strftime("%B"))[0].normal_form.title()
        category = operation.salary.name

        # Инициализируем структуру для категории
        if (
            category
            not in operations_old_by_year[year]["employees"][employee_id][
                "categories_by_month"
            ]
        ):
            operations_old_by_year[year]["employees"][employee_id][
                "categories_by_month"
            ][category] = {}
            operations_old_by_year[year]["employees"][employee_id][
                "operations_by_month"
            ][category] = {}

        # Добавляем операцию
        operations_old_by_year[year]["employees"][employee_id]["categories_by_month"][
            category
        ][month_name] = operation.amount
        operations_old_by_year[year]["employees"][employee_id]["operations_by_month"][
            category
        ][month_name] = operation.id

        # Обновляем total_by_month
        month_idx = MONTHS_RU.index(month_name)
        if category == "Оф ЗП (10 число)":
            # Для "Оф ЗП (10 число)" добавляем в следующий месяц
            if month_idx < len(MONTHS_RU) + 1:
                operations_old_by_year[year]["employees"][employee_id][
                    "total_by_month"
                ][month_idx - 1] += operation.amount
        else:
            operations_old_by_year[year]["employees"][employee_id]["total_by_month"][
                month_idx
            ] += operation.amount

    # Формируем groups_full для старых операций
    for year_data in operations_old_by_year.values():
        for employee_data in year_data["employees"].values():
            # Добавляем общую сумму для сотрудника
            employee_total = 0
            employee_data["groups_full"] = []

            # Считаем общие тоталы за год для долгов
            total_debt_issued = sum(
                value
                for key, value in employee_data["categories_by_month"]
                .get("Выдано в долг", {})
                .items()
                if key not in ["prev_month_values", "total"]
            )
            total_debt_returned = sum(
                value
                for key, value in employee_data["categories_by_month"]
                .get("Возврат долга", {})
                .items()
                if key not in ["prev_month_values", "total"]
            )
            total_debt_balance = total_debt_issued - total_debt_returned

            # Инициализируем total_by_month
            employee_data["total_by_month"] = [0] * len(MONTHS_RU)

            for group_name, group_categories in salary_groups.items():
                group_info = {
                    "name": group_name,
                    "categories": [],
                    "totals_by_month": [0] * len(MONTHS_RU),
                    "total_year": 0,
                }

                for category in group_categories:
                    if category == "Остаток долга":
                        cat_total = total_debt_balance
                        # Для Остаток долга используем общий баланс за год для всех месяцев
                        for month_idx in range(len(MONTHS_RU)):
                            group_info["totals_by_month"][
                                month_idx
                            ] = total_debt_balance
                    else:
                        cat_total = sum(
                            value
                            for key, value in employee_data["categories_by_month"]
                            .get(category, {})
                            .items()
                            if key not in ["prev_month_values", "total"]
                        )
                    bank_in = salary_groups_bank.get(category)
                    cat_in = cat_name_id.get(category)

                    group_info["categories"].append(
                        {
                            "name": category,
                            "name_id": cat_in,
                            "amount": cat_total,
                            "bank_in": bank_in,
                            "total_year": cat_total,
                        }
                    )

                    # Обновляем totals_by_month для группы
                    for month_idx, month in enumerate(MONTHS_RU):
                        if category == "Оф ЗП (10 число)":
                            # Для "Оф ЗП (10 число)" берем значение из предыдущего месяца
                            if month_idx > 0:
                                prev_month = MONTHS_RU[month_idx - 1]
                                amount = (
                                    employee_data["categories_by_month"]
                                    .get(category, {})
                                    .get(prev_month, 0)
                                )
                                group_info["totals_by_month"][month_idx] += amount
                                # Добавляем в общий тотал по месяцам
                                if group_name != "group4":
                                    employee_data["total_by_month"][month_idx] += amount
                        elif group_name == "group4":
                            # Для группы 4 (долги) используем общий баланс за год
                            group_info["totals_by_month"][
                                month_idx
                            ] = total_debt_balance
                        else:
                            amount = (
                                employee_data["categories_by_month"]
                                .get(category, {})
                                .get(month, 0)
                            )
                            group_info["totals_by_month"][month_idx] += amount
                            # Добавляем в общий тотал по месяцам
                            if group_name != "group4":
                                employee_data["total_by_month"][month_idx] += amount

                    # Добавляем в общий тотал группы
                    if group_name == "group4":
                        # Для group4 используем только разницу между выданными и возвращенными долгами
                        group_info["total_year"] = total_debt_balance
                    else:
                        group_info["total_year"] += cat_total
                        # Добавляем в общую сумму сотрудника
                        employee_total += cat_total

                employee_data["groups_full"].append(group_info)

            # Сохраняем общую сумму для сотрудника
            employee_data["total_year"] = employee_total

    # Преобразуем в список для шаблона
    operations_old_arr = []
    for year in sorted(operations_old_by_year.keys(), reverse=True):
        year_data = operations_old_by_year[year]
        year_info = {
            "year": year,
            "employees": list(year_data["employees"].values()),
        }

        # Добавляем date_start для каждого месяца в году
        for employee in year_info["employees"]:
            employee["months"] = []
            for month_idx, month in enumerate(MONTHS_RU):
                month_number = month_idx + 1
                date_start = datetime.datetime(year, month_number, 1)
                employee["months"].append(
                    {
                        "name": month,
                        "date_start": date_start,
                    }
                )

        operations_old_arr.append(year_info)

    # Итоги по всем сотрудникам по месяцам для каждой группы (для старых операций)
    totals_old_by_month = {}
    for year_data in operations_old_arr:
        year = year_data["year"]
        totals_old_by_month[year] = {
            "ИТОГО ЗП с ООО": [0] * len(MONTHS_RU),
            "ИТОГО ЗП с $": [0] * len(MONTHS_RU),
            "ИТОГО КВ $": [0] * len(MONTHS_RU),
            "ИТОГО КВ ИП": [0] * len(MONTHS_RU),
            "ИТОГО кварт. премия": [0] * len(MONTHS_RU),
            "Итого общий долг": [0] * len(MONTHS_RU),
            "total_year": {
                "ИТОГО ЗП с ООО": 0,
                "ИТОГО ЗП с $": 0,
                "ИТОГО КВ $": 0,
                "ИТОГО КВ ИП": 0,
                "ИТОГО кварт. премия": 0,
                "Итого общий долг": 0,
            },
        }

        # Словарь для хранения остатков долга по всем сотрудникам
        total_debt_balances = {}

        # Считаем общие тоталы за год для долгов
        total_debt_issued = 0
        total_debt_returned = 0

        for employee in year_data["employees"]:
            # Суммируем выданные долги
            total_debt_issued += sum(
                value
                for key, value in employee.get("categories_by_month", {})
                .get("Выдано в долг", {})
                .items()
                if key not in ["prev_month_values", "total"]
            )
            # Суммируем возвращенные долги
            total_debt_returned += sum(
                value
                for key, value in employee.get("categories_by_month", {})
                .get("Возврат долга", {})
                .items()
                if key not in ["prev_month_values", "total"]
            )

        # Общий остаток долга за год
        total_debt_balance = total_debt_issued - total_debt_returned

        # Расчет остатков долга по всем сотрудникам по месяцам
        for month_idx, month in enumerate(MONTHS_RU):
            # Получаем предыдущий месяц (если это не первый месяц)
            prev_month = MONTHS_RU[month_idx - 1] if month_idx > 0 else None

            # Получаем остаток предыдущего месяца
            prev_balance = total_debt_balances.get(prev_month, 0) if prev_month else 0

            # Суммируем операции по всем сотрудникам
            total_debt_issued = 0
            total_debt_returned = 0

            for employee in year_data["employees"]:
                total_debt_issued += (
                    employee.get("categories_by_month", {})
                    .get("Выдано в долг", {})
                    .get(month, 0)
                )
                total_debt_returned += (
                    employee.get("categories_by_month", {})
                    .get("Возврат долга", {})
                    .get(month, 0)
                )

            # Рассчитываем текущий остаток
            current_balance = prev_balance + total_debt_issued - total_debt_returned
            current_balance = max(0, current_balance)  # Не даем остатку уйти в минус

            # Сохраняем остаток
            total_debt_balances[month] = current_balance
            totals_old_by_month[year]["Итого общий долг"][month_idx] = current_balance

        for employee in year_data["employees"]:
            for group in employee["groups_full"]:
                if group["name"] == "group1":
                    # Для group1 (ООО) суммируем все категории
                    for month_idx, month in enumerate(MONTHS_RU):
                        for category in group["categories"]:
                            if category["name"] == "Оф ЗП (10 число)":
                                # Для "Оф ЗП (10 число)" берем значение из предыдущего месяца
                                if month_idx <= month_leng_total_month:
                                    prev_month = MONTHS_RU[month_idx + 1]
                                    amount = (
                                        employee.get("categories_by_month", {})
                                        .get(category["name"], {})
                                        .get(prev_month, 0)
                                    )
                                    totals_old_by_month[year]["ИТОГО ЗП с ООО"][
                                        month_idx
                                    ] += amount
                                    totals_old_by_month[year]["total_year"][
                                        "ИТОГО ЗП с ООО"
                                    ] += amount
                            else:
                                amount = (
                                    employee.get("categories_by_month", {})
                                    .get(category["name"], {})
                                    .get(month, 0)
                                )
                                totals_old_by_month[year]["ИТОГО ЗП с ООО"][
                                    month_idx
                                ] += amount
                                totals_old_by_month[year]["total_year"][
                                    "ИТОГО ЗП с ООО"
                                ] += amount
                elif group["name"] == "group2":
                    # Для group2 ($) суммируем все категории
                    for month_idx, total in enumerate(group["totals_by_month"]):
                        totals_old_by_month[year]["ИТОГО ЗП с $"][month_idx] += total
                    # Добавляем в общий тотал за год
                    totals_old_by_month[year]["total_year"]["ИТОГО ЗП с $"] += group[
                        "total_year"
                    ]
                elif group["name"] == "group3":
                    # Для group3 (КВ) распределяем по соответствующим категориям
                    for category in group["categories"]:
                        for month_idx, month in enumerate(MONTHS_RU):
                            amount = (
                                employee.get("categories_by_month", {})
                                .get(category["name"], {})
                                .get(month, 0)
                            )
                            if category["name"] == "КВ $":
                                totals_old_by_month[year]["ИТОГО КВ $"][
                                    month_idx
                                ] += amount
                                totals_old_by_month[year]["total_year"][
                                    "ИТОГО КВ $"
                                ] += amount
                            elif category["name"] == "КВ ИП":
                                totals_old_by_month[year]["ИТОГО КВ ИП"][
                                    month_idx
                                ] += amount
                                totals_old_by_month[year]["total_year"][
                                    "ИТОГО КВ ИП"
                                ] += amount
                            elif category["name"] == "квартальная премия":
                                totals_old_by_month[year]["ИТОГО кварт. премия"][
                                    month_idx
                                ] += amount
                                totals_old_by_month[year]["total_year"][
                                    "ИТОГО кварт. премия"
                                ] += amount
                elif group["name"] == "group4":
                    # Для group4 (долги) не добавляем в общие тоталы
                    pass

        # Добавляем общий тотал за год для долгов
        totals_old_by_month[year]["total_year"]["Итого общий долг"] = total_debt_balance

    # Преобразуем данные для шаблона
    employees_list = []
    for employee_id, data in employees_data.items():
        employee_info = {
            "employee": data["employee"],
            "months": [],
            "groups": [],
            "categories_by_month": {},
            "operations_by_month": {},
            "groups_full": [],
        }

        # Инициализация categories_by_month
        categories_by_month = {}
        operations_by_month = {}
        for group_name, group_data in data["groups"].items():
            for category, _ in group_data["categories"].items():
                if category not in categories_by_month:
                    categories_by_month[category] = {}
                    operations_by_month[category] = {}
                for month in months_current_year:
                    categories_by_month[category][month] = 0
                    operations_by_month[category][month] = None

        # Заполнение categories_by_month по операциям
        for month in months_current_year:
            month_data = data["months"][month]
            for op in month_data["operations"]:
                op_category = op.salary.name if hasattr(op.salary, "name") else None
                if op_category:
                    # Добавляем операцию в текущий месяц
                    categories_by_month.setdefault(op_category, {})
                    categories_by_month[op_category].setdefault(month, 0)
                    categories_by_month[op_category][month] += op.amount
                    operations_by_month.setdefault(op_category, {})
                    operations_by_month[op_category].setdefault(month, None)
                    operations_by_month[op_category][month] = op.id

                    # Если это "Оф ЗП (10 число)", добавляем в total следующего месяца
                    if op_category == "Оф ЗП (10 число)":
                        idx = months_current_year.index(month)
                        # Только если есть следующий месяц, переносим сумму
                        if idx < len(months_current_year) - 1:
                            next_month = months_current_year[idx + 1]
                            if "total" not in categories_by_month[op_category]:
                                categories_by_month[op_category]["total"] = {}
                            categories_by_month[op_category]["total"][
                                next_month
                            ] = op.amount
                        # Если текущий месяц последний (январь) — ничего не делаем

        # Добавляем предполагаемые траты на основе предыдущего месяца
        for category in categories_by_month:
            prev_month_values = {}
            for i, month in enumerate(months_current_year):
                if i < len(months_current_year) - 1:
                    prev_month = months_current_year[i + 1]
                    prev_value = categories_by_month[category].get(prev_month, 0)
                else:
                    prev_value = 0
                prev_month_values[month] = prev_value
            categories_by_month[category]["prev_month_values"] = prev_month_values

            # Обновляем total для операции "Оф ЗП (10 число)"
            if category == "Оф ЗП (10 число)":
                for month in months_current_year:
                    idx = months_current_year.index(month)
                    # Только если есть следующий месяц, переносим сумму
                    if idx < len(months_current_year) - 1:
                        next_month = months_current_year[idx + 1]
                        if next_month in categories_by_month[category]:
                            if "total" not in categories_by_month[category]:
                                categories_by_month[category]["total"] = {}
                            categories_by_month[category]["total"][month] = (
                                categories_by_month[category][next_month]
                            )
                    # Если текущий месяц последний (январь) — ничего не делаем

        employee_info["categories_by_month"] = categories_by_month
        employee_info["operations_by_month"] = operations_by_month

        # Формируем groups_full: всегда 4 группы, в каждой все категории из salary_groups
        groups_full = []
        for group_name, group_categories in salary_groups.items():
            group_info = {
                "name": group_name,
                "categories": [],
                "total": 0,
            }

            for category in group_categories:
                # Сумма по всем месяцам для этого сотрудника и категории
                cat_total = sum(
                    value
                    for key, value in categories_by_month.get(category, {}).items()
                    if key not in ["prev_month_values", "total"]
                )

                bank_in = salary_groups_bank.get(category)
                cat_in = cat_name_id.get(category)

                group_info["categories"].append(
                    {
                        "name": category,
                        "name_id": cat_in,
                        "amount": cat_total,
                        "bank_in": bank_in,
                    }
                )
                group_info["total"] += cat_total
            groups_full.append(group_info)
        employee_info["groups_full"] = groups_full

        # Итоги по месяцам для сотрудника
        total_by_month = []

        # Словарь для хранения остатков долга
        debt_balances = {}

        # Расчет остатка долга
        # Создаем список месяцев в правильном порядке (от января к текущему месяцу)
        months_ordered = []
        for month in range(1, month_now + 1):
            month_name = MONTHS_RU[month - 1]
            months_ordered.append(month_name)

        # Сначала рассчитываем остатки долга
        for i, month in enumerate(months_ordered):
            # Получаем предыдущий месяц (если это не первый месяц)
            prev_month = None
            if i > 0:
                prev_month = months_ordered[i - 1]

            # Получаем остаток предыдущего месяца
            prev_balance = debt_balances.get(prev_month, 0) if prev_month else 0

            # Получаем операции за текущий месяц
            debt_issued = (
                employee_info["categories_by_month"]
                .get("Выдано в долг", {})
                .get(month, 0)
            )
            debt_returned = (
                employee_info["categories_by_month"]
                .get("Возврат долга", {})
                .get(month, 0)
            )

            # Рассчитываем текущий остаток
            current_balance = prev_balance + debt_issued - debt_returned
            current_balance = max(0, current_balance)  # Не даем остатку уйти в минус

            # Сохраняем остаток в промежуточный словарь
            debt_balances[month] = current_balance

            # Сохраняем остаток в categories_by_month
            if "Остаток долга" not in employee_info["categories_by_month"]:
                employee_info["categories_by_month"]["Остаток долга"] = {}
            employee_info["categories_by_month"]["Остаток долга"][
                month
            ] = current_balance

        # Теперь рассчитываем общие суммы по месяцам в правильном порядке
        for month in months_current_year:
            idx = months_current_year.index(month)
            month_total = 0
            for group in employee_info["groups_full"]:
                if group["name"] != "group4":
                    for cat in group["categories"]:
                        if cat["name"] == "Оф ЗП (10 число)":
                            # Только если это не первый месяц (текущий месяц в списке)
                            if idx > 0:
                                prev_month = months_current_year[idx - 1]
                                month_total += (
                                    employee_info["categories_by_month"]
                                    .get(cat["name"], {})
                                    .get(prev_month, 0)
                                )
                            # Если это первый месяц — не учитываем вообще!
                        else:
                            month_total += (
                                employee_info["categories_by_month"]
                                .get(cat["name"], {})
                                .get(month, 0)
                            )
            total_by_month.append(month_total)

        employee_info["total_by_month"] = total_by_month

        # months_full: для каждого месяца — группы, для каждой группы — категории и total
        months_full = []
        for month in months_current_year:
            month_info = {"name": month, "groups": []}
            for group_name, group_categories in salary_groups.items():
                group_info = {
                    "name": group_name,
                    "categories": [],
                    "total": 0,
                }
                for category in group_categories:
                    amount = (
                        employee_info["categories_by_month"]
                        .get(category, {})
                        .get(month, 0)
                    )
                    group_info["categories"].append(
                        {"name": category, "amount": amount}
                    )
                    group_info["total"] += amount
                month_info["groups"].append(group_info)
            months_full.append(month_info)
        employee_info["months_full"] = months_full

        # Итоги по месяцам для каждой группы сотрудника
        group_month_totals = {}
        for group in employee_info["groups_full"]:
            group_month_totals[group["name"]] = []
            for month in months_current_year:
                idx = months_current_year.index(month)
                month_total = 0
                if group["name"] == "group4":
                    # Для группы 4 берем остаток долга
                    month_total = (
                        employee_info["categories_by_month"]
                        .get("Остаток долга", {})
                        .get(month, 0)
                    )
                else:
                    for cat in group["categories"]:
                        if cat["name"] == "Оф ЗП (10 число)":
                            # Только если это не первый месяц (текущий месяц в списке)
                            if idx > 0:
                                prev_month = months_current_year[idx - 1]
                                month_total += (
                                    employee_info["categories_by_month"]
                                    .get(cat["name"], {})
                                    .get(prev_month, 0)
                                )
                            # Если это первый месяц — не учитываем вообще!
                        else:
                            month_total += (
                                employee_info["categories_by_month"]
                                .get(cat["name"], {})
                                .get(month, 0)
                            )
                group_month_totals[group["name"]].append(month_total)
        employee_info["group_month_totals"] = group_month_totals

        # Добавляем месяцы
        i = 0
        for month in months_current_year:
            i += 1
            month_data = data["months"][month]
            # Определяем номер месяца
            month_number = MONTHS_RU.index(month) + 1
            # Устанавливаем дату начала для этого месяца
            date_start = datetime.datetime(year_now, month_number, 1)
            employee_info["months"].append(
                {
                    "name": month,
                    "date_start": date_start,
                    "group1_total": month_data["group1_total"],
                    "group2_total": month_data["group2_total"],
                    "group3_total": month_data["group3_total"],
                    "group4_total": month_data["group4_total"],
                    "operations": month_data["operations"],
                }
            )

        # Добавляем группы (оставляем для совместимости)
        for group_name, group_data in data["groups"].items():
            group_info = {
                "name": group_name,
                "total": group_data["total"],
                "categories": [],
            }
            for category, amount in group_data["categories"].items():
                group_info["categories"].append({"name": category, "amount": amount})
            employee_info["groups"].append(group_info)

        employees_list.append(employee_info)

    # Итоги по всем сотрудникам по месяцам для каждой группы
    totals_by_month = {
        "ИТОГО ЗП с ООО": [0 for _ in months_current_year],
        "ИТОГО ЗП с $": [0 for _ in months_current_year],
        "ИТОГО КВ $": [0 for _ in months_current_year],
        "ИТОГО КВ ИП": [0 for _ in months_current_year],
        "ИТОГО кварт. премия": [0 for _ in months_current_year],
        "Итого общий долг": [0 for _ in months_current_year],
    }
    #!!!ТУТ БЛОК ИТОГОВ ПО ВСЕМ СОТРУДНИКАМ
    for idx, month in enumerate(months_current_year):
        for employee in employees_list:
            # Итоги по ООО (group1)
            for category in employee["categories_by_month"]:
                if category == "Оф ЗП (10 число)":
                    # Только если это не первый месяц (текущий месяц в списке)
                    if idx > 0:
                        prev_month = months_current_year[idx - 1]
                        totals_by_month["ИТОГО ЗП с ООО"][idx] += employee[
                            "categories_by_month"
                        ][category].get(prev_month, 0)
                    # Если это первый месяц — не учитываем вообще!
                else:
                    totals_by_month["ИТОГО ЗП с ООО"][idx] += employee[
                        "categories_by_month"
                    ][category].get(month, 0)

            # Итоги по $ (group2)
            totals_by_month["ИТОГО ЗП с $"][idx] += employee["months"][idx][
                "group2_total"
            ]

            # Итоги по КВ $ и КВ ИП (из group3)
            for category in employee["categories_by_month"]:
                if category == "КВ $":
                    totals_by_month["ИТОГО КВ $"][idx] += employee[
                        "categories_by_month"
                    ][category].get(month, 0)
                elif category == "КВ ИП":
                    totals_by_month["ИТОГО КВ ИП"][idx] += employee[
                        "categories_by_month"
                    ][category].get(month, 0)
                elif category == "квартальная премия":
                    totals_by_month["ИТОГО кварт. премия"][idx] += employee[
                        "categories_by_month"
                    ][category].get(month, 0)

            # Итоги по долгам (group4) - используем group_month_totals
            totals_by_month["Итого общий долг"][idx] += employee["group_month_totals"][
                "group4"
            ][idx]

    # Получаем все категории GroupeSalary
    all_categories = list(all_categories_qs.values_list("name", flat=True))

    # Группируем категории по salary_groups и считаем total
    group_totals = {}
    for group_name, group_categories in salary_groups.items():
        group_totals[group_name] = []
        for category in group_categories:
            if category in all_categories:
                total = 0
                # Пропускаем категории из группы group4 (долги)
                if group_name != "group4":
                    for employee in employees_list:
                        for month in months_current_year:
                            total += (
                                employee["categories_by_month"]
                                .get(category, {})
                                .get(month, 0)
                            )
                group_totals[group_name].append({"name": category, "total": total})

    context = {
        "title": title,
        "type_url": type_url,
        "employees": employees_list,
        "months": months_current_year,
        "salary_groups": salary_groups,
        "totals_by_month": totals_by_month,
        "group_totals": group_totals,
        "year_now": str(year_now),
        "data_now": datetime.datetime.now(),
        "month_now_name": month_now_name,
        "operations_old": operations_old_arr,
        "totals_old_by_month": totals_old_by_month,
        "all_months": MONTHS_RU,
    }

    return render(request, "bank/inside/inside_one_salary.html", context)


def nalog(request):
    """
    Представление для отображения налоговых операций.

    """
    # Инициализация локали для корректного отображения русских названий месяцев
    locale.setlocale(locale.LC_ALL, "")

    # Инициализация морфологического анализатора для работы с русским языком
    morph = pymorphy3.MorphAnalyzer(lang="ru")

    # Базовые параметры
    title = "Налоги"
    type_url = "inside"
    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month
    if (
        request.COOKIES.get("sortOperAccount")
        and request.COOKIES.get("sortOperAccount") != "0"
    ):
        bank_id = request.COOKIES["sortOperAccount"]
        bank_id = [int(bank_id)]
    else:
        bank_id = [1, 2]

    # Получение всех категорий налогов с предварительной загрузкой связанных данных
    categoru_nalog = CategNalog.objects.filter(in_page_nalog=True).select_related(
        "bank_in"
    )

    # Формирование списка месяцев текущего года в обратном порядке
    months_current_year = [MONTHS_RU[month - 1] for month in range(1, month_now + 1)]
    months_current_year.reverse()

    # Создаем словарь для сопоставления названий месяцев с их номерами
    month_numbers = {month: i + 1 for i, month in enumerate(months_current_year)}

    # Инициализация структуры данных для хранения операций по категориям
    operations_by_category = {
        "OOO": {
            "name": "OOO",
            "name_full": "OOO  (без УСН)",
            "full_year_total": 0,
            "sections": {
                "Налоги с ЗП": {
                    "name": "Налоги с ЗП",
                    "category": [],
                    "totals_month": {},
                    "full_year_total": 0,
                },
                "Прочие налоги": {
                    "name": "Прочие налоги",
                    "category": [],
                    "totals_month": {},
                    "full_year_total": 0,
                },
            },
            "totals_month": {},
        },
        "ИП": {
            "name": "ИП (откладываем до оплаты)",
            "name_full": "ИП",
            "full_year_total": 0,
            "category": [],
            "totals_month": {},
        },
        "total_all": {
            "name": "ИТОГО",
            "name_full": "ИТОГО",
            "full_year_total": 0,
            "totals_month": {},
        },
    }

    # Инициализация totals_month для общего итога
    for i, month in enumerate(months_current_year):
        operations_by_category["total_all"]["totals_month"][month] = {
            "total": 0,
            "expected": 0,
            "month_number": len(months_current_year) - i,
            "date_start": datetime.datetime(year_now, len(months_current_year) - i, 1),
        }

    # Инициализация totals_month для каждого типа банка и секции
    for bank_type, bank_data in operations_by_category.items():
        if bank_type == "OOO":
            # Инициализация для ООО
            for section_name, section_data in bank_data["sections"].items():
                for i, month in enumerate(months_current_year):
                    section_data["totals_month"][month] = {
                        "total": 0,
                        "expected": 0,
                        "month_number": len(months_current_year) - i,
                        "date_start": datetime.datetime(
                            year_now, len(months_current_year) - i, 1
                        ),
                        "operation_id": 0,
                    }
            # Инициализация общего итога для ООО
            for i, month in enumerate(months_current_year):
                bank_data["totals_month"][month] = {
                    "total": 0,
                    "expected": 0,
                }
        else:
            # Инициализация для ИП и общего итога
            for i, month in enumerate(months_current_year):
                bank_data["totals_month"][month] = {
                    "total": 0,
                    "expected": 0,
                    "month_number": len(months_current_year) - i,
                    "date_start": datetime.datetime(
                        year_now, len(months_current_year) - i, 1
                    ),
                }

    # Формирование структуры данных для категорий налогов
    for cat in categoru_nalog:
        arr = {
            "cat_name": cat.name,
            "cat_id": cat.id,
            "cat_bank_in": cat.bank_in.id,
            "cat_bank_in_name": cat.bank_in.name,
            "months": {},
            "full_year_total": 0,
        }

        # Инициализация месяцев для каждой категории
        for i, month in enumerate(months_current_year):
            arr["months"][month] = {
                "month_name": month,
                "month_data": "",
                "total": 0,
                "expected": 0,
                "month_number": len(months_current_year) - i,
                "date_start": datetime.datetime(
                    year_now, len(months_current_year) - i, 1
                ),
                "operation_id": 0,
            }

        # Распределение категорий по типам банков и секциям
        if cat.bank_in.id == 1:  # ООО
            section = (
                "Налоги с ЗП"
                if cat.name != "налог на аренду офиса"
                else "Прочие налоги"
            )
            operations_by_category["OOO"]["sections"][section]["category"].append(arr)
        elif cat.bank_in.id == 2:  # ИП
            operations_by_category["ИП"]["category"].append(arr)

    # Получение операций за текущий год
    operations = (
        Operation.objects.filter(
            nalog__isnull=False,
            data__year__gte=year_now,
        )
        .select_related("nalog", "nalog__bank_in")
        .prefetch_related()
        .order_by("-data")
    )

    # Обработка операций текущего года
    for operation in operations:
        if not operation.nalog:
            continue

        month_name = MONTHS_RU[operation.data.month - 1]
        bank_type = "OOO" if operation.nalog.bank_in.id == 1 else "ИП"

        if bank_type == "OOO":
            # Обработка операций ООО
            section = (
                "Налоги с ЗП"
                if operation.nalog.name != "налог на аренду офиса"
                else "Прочие налоги"
            )

            for category in operations_by_category[bank_type]["sections"][section][
                "category"
            ]:
                if category["cat_id"] == operation.nalog.id:
                    # Обновление данных для месяца
                    category["months"][month_name].update(
                        {
                            "month_data": operation,
                            "total": operation.amount,
                            "operation_id": operation.id,
                        }
                    )

                    # Обновление итогов
                    operations_by_category[bank_type]["sections"][section][
                        "totals_month"
                    ][month_name].update(
                        {
                            "total": operations_by_category[bank_type]["sections"][
                                section
                            ]["totals_month"][month_name]["total"]
                            + operation.amount,
                            "operation_id": operation.id,
                        }
                    )
                    operations_by_category[bank_type]["totals_month"][month_name][
                        "total"
                    ] += operation.amount
                    category["full_year_total"] += operation.amount
                    break
        else:
            # Обработка операций ИП
            for category in operations_by_category[bank_type]["category"]:
                if category["cat_id"] == operation.nalog.id:
                    category["months"][month_name].update(
                        {
                            "month_data": operation,
                            "total": operation.amount,
                            "operation_id": operation.id,
                        }
                    )
                    operations_by_category[bank_type]["totals_month"][month_name][
                        "total"
                    ] += operation.amount
                    category["full_year_total"] += operation.amount
                    break

    # Расчет ожидаемых расходов и итогов
    for bank_type, bank_data in operations_by_category.items():
        if bank_type == "OOO":
            for section_name, section_data in bank_data["sections"].items():
                # Расчет итогов за год для секции
                section_data["full_year_total"] = sum(
                    month_data["total"]
                    for month_data in section_data["totals_month"].values()
                )

                # Расчет ожидаемых расходов
                for i, month in enumerate(months_current_year):
                    if i < len(months_current_year) - 1:
                        prev_month = months_current_year[i + 1]
                        section_data["totals_month"][month]["expected"] = section_data[
                            "totals_month"
                        ][prev_month]["total"]

                        for category in section_data["category"]:
                            category["months"][month]["expected"] = category["months"][
                                prev_month
                            ]["total"]

            # Обновление общих ожидаемых расходов для ООО
            for i, month in enumerate(months_current_year):
                if i < len(months_current_year) - 1:
                    prev_month = months_current_year[i + 1]
                    bank_data["totals_month"][month]["expected"] = bank_data[
                        "totals_month"
                    ][prev_month]["total"]

            # Расчет итога за год для ООО
            bank_data["full_year_total"] = sum(
                month_data["total"] for month_data in bank_data["totals_month"].values()
            )
        elif bank_type == "ИП":
            # Расчет ожидаемых расходов и итогов для ИП
            for i, month in enumerate(months_current_year):
                if i < len(months_current_year) - 1:
                    prev_month = months_current_year[i + 1]
                    bank_data["totals_month"][month]["expected"] = bank_data[
                        "totals_month"
                    ][prev_month]["total"]

                    for category in bank_data["category"]:
                        category["months"][month]["expected"] = category["months"][
                            prev_month
                        ]["total"]

            bank_data["full_year_total"] = sum(
                month_data["total"] for month_data in bank_data["totals_month"].values()
            )
        elif bank_type == "total_all":
            # Расчет общих итогов
            for month in months_current_year:
                ooo_total = operations_by_category["OOO"]["totals_month"][month][
                    "total"
                ]
                ip_total = operations_by_category["ИП"]["totals_month"][month]["total"]
                operations_by_category["total_all"]["totals_month"][month]["total"] = (
                    ooo_total + ip_total
                )

            operations_by_category["total_all"]["full_year_total"] = sum(
                month_data["total"]
                for month_data in operations_by_category["total_all"][
                    "totals_month"
                ].values()
            )

    # СТАРЫЕ ОПЕРАЦИИ
    # Получение исторических операций
    operations_old = (
        Operation.objects.filter(
            nalog__isnull=False,
            data__year__lt=year_now,
        )
        .select_related("nalog", "nalog__bank_in")
        .prefetch_related()
        .order_by("-data")
    )

    # Инициализация структуры для исторических операций
    operations_old_by_year = {"OOO": {}, "ИП": {}, "total_all": {}}

    # Получение уникальных годов из исторических операций
    years_with_operations = {operation.data.year for operation in operations_old}

    # Формирование структуры данных для каждого года
    for year in sorted(years_with_operations, reverse=True):
        # Инициализация структуры для ООО
        operations_old_by_year["OOO"][year] = {
            "year": year,
            "name": "OOO",
            "name_full": "OOO  (без УСН)",
            "full_year_total": 0,
            "sections": {
                "Налоги с ЗП": {
                    "name": "Налоги с ЗП",
                    "category": [],
                    "totals_month": {},
                    "full_year_total": 0,
                },
                "Прочие налоги": {
                    "name": "Прочие налоги",
                    "category": [],
                    "totals_month": {},
                    "full_year_total": 0,
                },
            },
            "totals_month": {},
        }

        # Инициализация структуры для ИП
        operations_old_by_year["ИП"][year] = {
            "year": year,
            "name": "ИП (откладываем до оплаты)",
            "name_full": "ИП",
            "full_year_total": 0,
            "category": [],
            "totals_month": {},
        }

        # Инициализация структуры для общего итога
        operations_old_by_year["total_all"][year] = {
            "year": year,
            "name": "Итого",
            "name_full": "Итого год",
            "full_year_total": 0,
            "totals_month": {},
        }

        # Инициализация месяцев для всех структур
        for month in MONTHS_RU:
            # Для ООО
            operations_old_by_year["OOO"][year]["totals_month"][month] = {"total": 0}

            # Для секций ООО
            for section in operations_old_by_year["OOO"][year]["sections"].values():
                section["totals_month"][month] = {
                    "total": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "date_start": datetime.datetime(
                        year, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                }

            # Для ИП
            operations_old_by_year["ИП"][year]["totals_month"][month] = {
                "total": 0,
                "month_number": MONTHS_RU.index(month) + 1,
                "date_start": datetime.datetime(year, MONTHS_RU.index(month) + 1, 1),
            }

        # Инициализация категорий для ООО
        for cat in categoru_nalog:
            if cat.bank_in.id == 1:
                section = (
                    "Налоги с ЗП"
                    if cat.name != "налог на аренду офиса"
                    else "Прочие налоги"
                )
                arr = {
                    "cat_name": cat.name,
                    "cat_id": cat.id,
                    "cat_bank_in": cat.bank_in.id,
                    "cat_bank_in_name": cat.bank_in.name,
                    "months": {},
                    "full_year_total": 0,
                }

                # Инициализация месяцев для категории
                for month in MONTHS_RU:
                    arr["months"][month] = {
                        "month_name": month,
                        "month_data": "",
                        "total": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "date_start": datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        ),
                        "operation_id": 0,
                    }
                operations_old_by_year["OOO"][year]["sections"][section][
                    "category"
                ].append(arr)

        # Инициализация категорий для ИП
        for cat in categoru_nalog:
            if cat.bank_in.id == 2:
                arr = {
                    "cat_name": cat.name,
                    "cat_id": cat.id,
                    "cat_bank_in": cat.bank_in.id,
                    "cat_bank_in_name": cat.bank_in.name,
                    "months": {},
                    "full_year_total": 0,
                }

                # Инициализация месяцев для категории
                for month in MONTHS_RU:
                    arr["months"][month] = {
                        "month_name": month,
                        "month_data": "",
                        "total": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "date_start": datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        ),
                        "operation_id": 0,
                    }
                operations_old_by_year["ИП"][year]["category"].append(arr)

    # Обработка исторических операций
    for operation in operations_old:
        if not operation.nalog:
            continue

        year = operation.data.year
        month_name = MONTHS_RU[operation.data.month - 1]
        bank_type = "OOO" if operation.nalog.bank_in.id == 1 else "ИП"
        year_data = operations_old_by_year[bank_type][year]

        if bank_type == "OOO":
            # Обработка операций ООО
            section = (
                "Налоги с ЗП"
                if operation.nalog.name != "налог на аренду офиса"
                else "Прочие налоги"
            )
            section_data = year_data["sections"][section]

            for category in section_data["category"]:
                if category["cat_id"] == operation.nalog.id:
                    # Обновление данных для месяца
                    month_data = category["months"][month_name]
                    month_data.update(
                        {
                            "month_data": operation,
                            "total": operation.amount,
                            "operation_id": operation.id,
                        }
                    )

                    # Обновление итогов
                    section_data["totals_month"][month_name].update(
                        {
                            "total": section_data["totals_month"][month_name]["total"]
                            + operation.amount,
                            "operation_id": operation.id,
                        }
                    )
                    year_data["totals_month"][month_name]["total"] += operation.amount
                    category["full_year_total"] += operation.amount
                    break
        else:
            # Обработка операций ИП
            for category in year_data["category"]:
                if category["cat_id"] == operation.nalog.id:
                    month_data = category["months"][month_name]
                    month_data.update(
                        {
                            "month_data": operation,
                            "total": operation.amount,
                            "operation_id": operation.id,
                        }
                    )
                    year_data["totals_month"][month_name]["total"] += operation.amount
                    category["full_year_total"] += operation.amount
                    break

    # Расчет итогов за год для исторических данных
    for bank_type in ["OOO", "ИП"]:
        for year, year_data in operations_old_by_year[bank_type].items():
            if bank_type == "OOO":
                # Расчет итогов для ООО
                ooo_total = 0
                for section_name, section_data in year_data["sections"].items():
                    section_total = sum(
                        month_data["total"]
                        for month_data in section_data["totals_month"].values()
                    )
                    section_data["full_year_total"] = section_total
                    ooo_total += section_total
                year_data["full_year_total"] = ooo_total
            else:
                # Расчет итогов для ИП
                year_data["full_year_total"] = sum(
                    month_data["total"]
                    for month_data in year_data["totals_month"].values()
                )

    # Расчет общего итога для исторических операций по годам
    for year in years_with_operations:
        # Инициализация структуры для общего итога за год
        operations_old_by_year["total_all"][year] = {
            "year": year,
            "name": "Итого",
            "name_full": "Итого год",
            "full_year_total": 0,
            "totals_month": {},
        }

        # Инициализация месяцев для общего итога
        for month in MONTHS_RU:
            operations_old_by_year["total_all"][year]["totals_month"][month] = {
                "total": 0,
                "month_number": MONTHS_RU.index(month) + 1,
                "date_start": datetime.datetime(year, MONTHS_RU.index(month) + 1, 1),
            }

        # Расчет итогов по месяцам
        for month in MONTHS_RU:
            # Суммируем значения из ООО и ИП для каждого месяца
            ooo_total = operations_old_by_year["OOO"][year]["totals_month"][month][
                "total"
            ]
            ip_total = operations_old_by_year["ИП"][year]["totals_month"][month][
                "total"
            ]
            operations_old_by_year["total_all"][year]["totals_month"][month][
                "total"
            ] = (ooo_total + ip_total)

        # Расчет общего итога за год
        operations_old_by_year["total_all"][year]["full_year_total"] = sum(
            month_data["total"]
            for month_data in operations_old_by_year["total_all"][year][
                "totals_month"
            ].values()
        )

    # Формирование контекста для шаблона
    context = {
        "title": title,
        "type_url": type_url,
        "operations_by_category": operations_by_category,
        "operations_old_by_year": operations_old_by_year,
        "year_now": year_now,
        "nalog_wr_old": operations_old_by_year[
            "total_all"
        ],  # Добавляем общие итоги по годам
    }

    return render(request, "bank/inside/inside_one_nalog.html", context)


# Внешние счета
def outside(request):
    title = "Внешнии счета"
    type_url = "outside"
    context = {
        "title": title,
        "type_url": type_url,
    }

    return render(request, "bank/outside/outside_all.html", context)


def outside_ooo(request):
    locale.setlocale(locale.LC_ALL, "")
    title = "OOO"
    type_url = "outside"
    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month
    # Получаем только нужный банк
    bank = Bank.objects.get(id=1)

    services = Service.objects.all()
    categoru_nalog = CategNalog.objects.filter(
        in_page_nalog=False, bank_in=bank
    ).values("id", "name")

    names_btw = [
        "ПРЕМИИ",
        "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП",
        "перевод на ИП для оплаты субподряда",
    ]
    cate_oper_beetwen = CategOperationsBetweenBank.objects.filter(
        bank_in=bank, name__in=names_btw
    ).values("id", "name", "bank_in", "bank_to")
    cate_oper_beetwen_by_name = {item["name"]: item for item in cate_oper_beetwen}

    names = [
        "ПРИБЫЛЬ 1% ЦРП 5%",
        "КВ 20% ЦРП 50%",
        "НАЛОГ УСН ООО доход-расходы*15% ЦРП 2- ТРП 1,5% (отложенные на выплату)",
        "Реальный налог УСН с ООО доход - 1%",
    ]

    categ_percents = CategForPercentGroupBank.objects.filter(
        bank=bank, name__in=names
    ).values("id", "name", "bank", "category_between", "category_between__bank_to")
    categ_percent_by_name = {item["name"]: item for item in categ_percents}

    categ_percent_value = (
        CategPercentGroupBank.objects.select_related(
            "category", "bank", "bank_categpercentgroupbank_name"
        )
        .annotate(month=ExtractMonth("data"))
        .values("id", "category", "data", "percent", "category_id")
    )
    categ_percent_list = list(categ_percent_value)

    operations = (
        Operation.objects.select_related(
            "bank_in",
            "bank_to",
            "operaccount",
            "salary",
            "nalog",
            "employee",
            "monthly_bill",
            "monthly_bill__service",
            "suborder",
            "suborder__month_bill",
            "suborder__month_bill__service",
            "suborder__platform",
            "suborder__category_employee",
            "suborder_other",
            "between_bank",
        )
        .filter(
            Q(bank_in=bank) | Q(bank_to=bank),
            data__year__gte=year_now,
        )
        .order_by("data")
    )
    operations_old = (
        Operation.objects.select_related(
            "bank_in",
            "bank_to",
            "operaccount",
            "salary",
            "nalog",
            "employee",
            "monthly_bill",
            "monthly_bill__service",
            "suborder",
            "suborder__month_bill",
            "suborder__month_bill__service",
            "suborder__platform",
            "suborder__category_employee",
            "suborder_other",
            "between_bank",
        )
        .filter(
            Q(bank_in=bank) | Q(bank_to=bank),
            data__year__lt=year_now,
        )
        .order_by("data")
    )

    # Получаем все сервисы одним запросом
    services = Service.objects.all().select_related()
    other_categ_subkontract = SubcontractOtherCategory.objects.filter(
        bank=bank
    ).exclude(name="Topvisor")

    # Создаем список месяцев текущего года
    months_current_year = [MONTHS_RU[month - 1] for month in range(1, month_now + 1)]

    months_current_year.reverse()

    # Создаем словарь для сопоставления названий месяцев с их номерами
    month_numbers = {month: i + 1 for i, month in enumerate(months_current_year)}

    months_current_year_old = MONTHS_RU.copy()
    months_current_year_old.reverse()
    month_numbers_old = {
        month: i + 1 for i, month in enumerate(months_current_year_old)
    }

    # СТАРТОВЫЕ МАССИВЫ
    # Р/С на начало месяца
    arr_start_month = {
        "name": "Р/С на начало месяца",
        "total": {},
    }
    # ПОСТУПЛЕНИЯ
    arr_in = {
        "name": "ПОСТУПЛЕНИЯ",
        "category": [
            {
                "name": "по договорам услуг",
                "group": {},
            },
            {
                "name": "между счетами:",
                "group": {
                    "перевод с ИП для оплаты субподряда": {},
                    "перевод с $ для оплаты субподряда": {},
                    "зачисление из хранилища": {},
                },
            },
        ],
        "total_category": {
            "name": "ИТОГО ПОСТУПЛЕНИЯ",
            "total": {},
        },
    }
    # СУБПОДРЯДЧИКИ + ПЛОЩАДКИ, в т.ч.
    arr_out = {
        "name": "СУБПОДРЯДЧИКИ + ПЛОЩАДКИ, в т.ч.",
        "category": [
            {
                "name": "по договорам услуг",
                "group": {
                    "SEO": {
                        "Topvisor": {},
                        "ИП Галаев": {},
                        "Другое": {},
                    },
                    "остальное": {},
                },
            },
            {
                "name": "между счетами:",
                "group": {
                    "перевод на ИП для оплаты субподряда": {},
                },
            },
            {
                "name": "другие субподряды:",
                "group": {},
            },
        ],
        "total_category": {
            "name": "ИТОГО СУБПОДРЯДЧИКИ + ПЛОЩАДКИ",
            "total": {},
        },
    }

    # петвый блок ДОХОД-РАСХОД
    arr_in_out_all = {
        "name": None,
        "category": [
            {
                "name": "РЕАЛЬНЫЕ ПОСТУПЛЕНИЯ ООО (ВЫРУЧКА-СУБПОДРЯД И БУХ)",
                "total": {},
            },
            {
                "name": "ПРИБЫЛЬ 1% ЦРП 5%",
                "total": {},
            },
            {
                "name": "КВ 20% ЦРП 50%",
                "total": {},
            },
            {
                "name": "ПРЕМИИ",
                "total": {},
            },
            {
                "name": "ИТОГО",
                "total": {},
            },
            {
                "name": "ПРОВЕРКА ООО ДОХОД-РАСХОД = ОСТАТОК",
                "total": {},
            },
        ],
    }

    # второй блок ДОХОД-РАСХОД
    arr_in_out_after_all = {
        "name": None,
        "category": [
            {
                "name": "ДОХОД - РЕАЛЬНЫЙ РАСХОД в текущем месяце",
                "total": {},
            },
            {
                "name": "НАЛОГ УСН ООО доход-расходы*15% ЦРП 2- ТРП 1,5% (отложенные на выплату)",
                "total": {},
            },
            {
                "name": "Реальный налог УСН с ООО доход - 1%",
                "total": {},
            },
            {
                "name": "ПРОВЕРКА ДОХОД - РАСХОД",
                "total": {},
            },
        ],
    }

    # третий йблок ДОХОД-РАСХОД
    arr_in_out_after_all_total = {
        "name": None,
        "category": [
            {
                "name": "ДОХОД-РАСХОД (в текущем месяце без УСН и вывода остатков)",
                "total": {},
            },
            {
                "name": "ФАКТИЧЕСКАЯ ОПЛАТА УСН",
                "total": {},
            },
            {
                "name": "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП",
                "total": {},
            },
            {
                "name": "ОСТАТОК на Р/С на конец месяца (после уплаты УСН и вывода остатков)",
                "total": {},
            },
        ],
    }

    # ВНУТРЕННИЕ СЧЕТА
    arr_inside_all = {
        "name": "ВНУТРЕННИЕ СЧЕТА",
        "category": [
            {
                "name": "НАЛОГИ (без УСН):",
                "group": {
                    "ИТОГО налоги с ЗП:": {},
                },
                "total": {
                    "name": "ВЫПЛАЧЕННЫЕ НАЛОГИ (без УСН)",
                    "total": {},
                },
            },
            {
                "name": "ЗП с ООО",
                "total": {
                    "name": "ИТОГО ЗП с ООО",
                    "total": {},
                },
            },
            {
                "name": "ОПЕР СЧЕТ, в т.ч.:",
                "group": {},
                "total": {
                    "name": "ИТОГО ОПЕР СЧЁТ",
                    "total": {},
                },
            },
        ],
        "total_category": {
            "name": "ИТОГО РАСХОДЫ ВНУТРЕННИЕ СЧЕТА",
            "total": {},
        },
    }
    
    arr_start_month_old = copy.deepcopy(arr_start_month)
    arr_in_old = copy.deepcopy(arr_in)
    arr_out_old = copy.deepcopy(arr_out)
    arr_in_out_all_old = copy.deepcopy(arr_in_out_all)
    arr_in_out_after_all_old = copy.deepcopy(arr_in_out_after_all)
    arr_in_out_after_all_total_old = copy.deepcopy(arr_in_out_after_all_total)
    arr_inside_all_old = copy.deepcopy(arr_inside_all)
   
    old_oper_arr = {}
    
    old_oper_arr = fill_operations_arrays_ooo(
        operations_old,
        arr_in_old,
        arr_out_old,
        arr_in_out_all_old,
        arr_inside_all_old,
        arr_in_out_after_all_old,
        arr_in_out_after_all_total_old,
        arr_start_month_old,
        months_current_year_old,
        year_now,
        bank,
        get_id_categ_oper,
        CATEGORY_OPERACCOUNT,
        MONTHS_RU,
        cate_oper_beetwen_by_name,
        categ_percent_by_name,
        categoru_nalog,
        month_numbers_old,
        categ_percent_list,
        services,
        other_categ_subkontract,
        is_old_oper=True,
        old_oper_arr=None,
    )

    (
        arr_in,
        arr_out,
        arr_in_out_all,
        arr_inside_all,
        arr_in_out_after_all,
        arr_in_out_after_all_total,
        arr_start_month,
    ) = fill_operations_arrays_ooo(
        operations,
        arr_in,
        arr_out,
        arr_in_out_all,
        arr_inside_all,
        arr_in_out_after_all,
        arr_in_out_after_all_total,
        arr_start_month,
        months_current_year,
        year_now,
        bank,
        get_id_categ_oper,
        CATEGORY_OPERACCOUNT,
        MONTHS_RU,
        cate_oper_beetwen_by_name,
        categ_percent_by_name,
        categoru_nalog,
        month_numbers,
        categ_percent_list,
        services,
        other_categ_subkontract,
        is_old_oper=False,
        old_oper_arr=old_oper_arr,
    )
    
    # Пример для формирования и чтения кеша для банка
    cache_key = f"bank_{bank.id}_context_{year_now}"
    
    context_cash = cache.get(cache_key)
    print(f"Пробуем получить из кеша: {cache_key}")
    context_cash = cache.get(cache_key)
    print(f"Из кеша получено: {context_cash}")
    if not context_cash:
        print(f"Кеш пустой, формируем новый context_cash для ключа {cache_key}")
        context_cash = {
            "title": title,
            "year_now": year_now,
            "type_url": type_url,
            "bank": bank.id,
            # "arr_in": arr_in,
            # "arr_out": arr_out,
            "arr_in_out_all": arr_in_out_all,
            # "arr_inside_all": arr_inside_all,
            # "arr_in_out_after_all": arr_in_out_after_all,
            # "arr_in_out_after_all_total": arr_in_out_after_all_total,
            # "arr_start_month": arr_start_month,
            # "old_oper_arr": old_oper_arr,
        }
        print(f"Сохраняем в кеш: {context_cash}")
        cache.set(cache_key, context_cash, 60*60)
    else:
        print(f"Кеш найден для ключа {cache_key}") 

    context = {
        "title": title,
        "year_now": year_now,
        "type_url": type_url,
        "bank": bank.id,
        "arr_in": arr_in,
        "arr_out": arr_out,
        "arr_in_out_all": arr_in_out_all,
        "arr_inside_all": arr_inside_all,
        "arr_in_out_after_all": arr_in_out_after_all,
        "months_current_year": months_current_year,
        "arr_in_out_after_all_total": arr_in_out_after_all_total,
        "arr_start_month": arr_start_month,
            "old_oper_arr": old_oper_arr,
    }

    return render(request, "bank/outside/outside_ooo.html", context)


def outside_ip(request):
    from django.core.cache import cache
    locale.setlocale(locale.LC_ALL, "")
    title = "ИП"
    type_url = "outside"
    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month
    # Получаем только нужный банк
    bank = Bank.objects.get(id=2)
    categoru_nalog = CategNalog.objects.filter(
        in_page_nalog=False, bank_in=bank
    ).values("id", "name")
    operations = (
        Operation.objects.select_related(
            "bank_in",
            "bank_to",
            "operaccount",
            "salary",
            "nalog",
            "employee",
            "monthly_bill",
            "monthly_bill__service",
            "suborder",
            "suborder__month_bill",
            "suborder__month_bill__service",
            "suborder__platform",
            "suborder__category_employee",
            "suborder_other",
            "between_bank",
        )
        .filter(
            Q(bank_in=bank) | Q(bank_to=bank),
            data__year__gte=year_now,
        )
        .order_by("data")
    )
    operations_old = (
        Operation.objects.select_related(
            "bank_in",
            "bank_to",
            "operaccount",
            "salary",
            "nalog",
            "employee",
            "monthly_bill",
            "monthly_bill__service",
            "suborder",
            "suborder__month_bill",
            "suborder__month_bill__service",
            "suborder__platform",
            "suborder__category_employee",
            "suborder_other",
            "between_bank",
        )
        .filter(
            Q(bank_in=bank) | Q(bank_to=bank),
            data__year__lt=year_now,
        )
        .order_by("data")
    )
    # Создаем список месяцев текущего года
    months_current_year = [MONTHS_RU[month - 1] for month in range(1, month_now + 1)]
    months_current_year.reverse()
    # Создаем словарь для сопоставления названий месяцев с их номерами
    month_numbers = {month: i + 1 for i, month in enumerate(months_current_year)}

    services = Service.objects.all()
    
    other_categ_subkontract = SubcontractOtherCategory.objects.filter(bank=bank)
    names_btw = [
        "вывод $ для оплаты субподряда (вручную)",
        "вывод остатков ООО в Хранилище",
        "остаток ПРИБЫЛЬ 1% ЦРП 5%",
        "остаток КВ 0,5 % ЦРП 50%"
    ]
    cate_oper_beetwen = CategOperationsBetweenBank.objects.filter(
        bank_in=bank, name__in=names_btw
    ).values("id", "name", "bank_in", "bank_to")
    cate_oper_beetwen_by_name = {item["name"]: item for item in cate_oper_beetwen}
    
    names = [
        "ПРИБЫЛЬ 1% ЦРП 5%",
        "КВ 20% ЦРП 50%",
        "на квартальную премию собственникам",
        "компенсация владельцу с ИП",
    ]
    categ_percents = CategForPercentGroupBank.objects.filter(
        bank=bank, name__in=names
    ).values("id", "name", "bank", "category_between", "category_between__bank_to")
    categ_percent_by_name = {item["name"]: item for item in categ_percents}
    
    categ_percent_value = (
        CategPercentGroupBank.objects.select_related(
            "category", "bank", "bank_categpercentgroupbank_name"
        )
        .annotate(month=ExtractMonth("data"))
        .values("id", "category", "data", "percent", "category_id")
    )
    categ_percent_list = list(categ_percent_value)

    # СТАРТОВЫЕ МАССИВЫ
    # Р/С на начало месяца
    arr_start_month_ip = {
        "name": "Р/С на начало месяца",
        "total": {},
    }
    # ПОСТУПЛЕНИЯ
    arr_in_ip = {
        "name": "ПОСТУПЛЕНИЯ",
        "category": [
            {
                "name": "по договорам услуг",
                "group": {},
            },
            {
                "name": "между счетами:",
                "group": {
                    "ООО прибыль ЦРП 5%": {},
                    "ООО КВ ЦРП 50%": {},
                    "на премии": {},
                    "перевод с ООО для оплаты субподряда": {},
                    "зачисление $ для оплаты субподряда": {},
                    "зачисление из хранилища": {},
                    "ПЕРЕВОД ОСТАТКОВ С ООО": {},
                },
            },
        ],
        "total_category": {
            "name": "ИТОГО ПОСТУПЛЕНИЯ",
            "total": {},
        },
    }
    # СУБПОДРЯДЧИКИ + ПЛОЩАДКИ, в т.ч.
    arr_out_ip = {
        "name": "СУБПОДРЯДЧИКИ + ПЛОЩАДКИ, в т.ч.",
        "category": [
            {
                "name": "по договорам услуг",
                "group": {},
            },
            {
                "name": "между счетами:",
                "group": {
                    "вывод $ для оплаты субподряда (вручную)": {},
                    "вывод остатков ООО в Хранилище": {},
                },
            },
            {
                "name": "другие субподряды:",
                "group": {},
            },
        ],
        "total_category": {
            "name": "ИТОГО СУБПОДРЯДЧИКИ + ПЛОЩАДКИ",
            "total": {},
        },
    }

    # петвый блок ДОХОД-РАСХОД
    arr_in_out_all_ip = {
        "name": None,
        "category": [
          
            {
                "name": "ПРИБЫЛЬ 1% ЦРП 5%",
                "total": {},
            },
            {
                "name": "КВ 20% ЦРП 50%",
                "total": {},
            },
            {
                "name": "ПРЕМИИ",
                "total": {},
            },
            {
                "name": "всего выводим с ИП (премии+КВ+остатки)",
                "total": {},
            },
            {
                "name": "ПРОВЕРКА",
                "total": {},
            },
        ],
    }

    # РЕАЛЬНЫЕ ПОСТУПЛЕНИЯ ИП (ВЫРУЧКА-СУБПОДРЯД)
    arr_real_diff_ip = {
        "name": "РЕАЛЬНЫЕ ПОСТУПЛЕНИЯ ИП (ВЫРУЧКА-СУБПОДРЯД)",
        "total": {},
    }
    # ВНУТРЕННИЕ СЧЕТА
    arr_inside_all_ip = {
        "name": "ВНУТРЕННИЕ СЧЕТА",
        "category": [
            #
            {
                "name": "НАЛОГИ ИП (откладываем до оплаты)",
                "total": {
                    "name": "ИТОГО налоги на ИП",
                    "total": {},
                },
            },
            {
                "name": "ОПЕР СЧЕТ, в т.ч.:",
                "group": {},
                "total": {
                    "name": "ИТОГО ОПЕР СЧЁТ",
                    "total": {},
                },
            },
        ],
        "total_category": {
            "name": "ИТОГО РАСХОДЫ ВНУТРЕННИЕ СЧЕТА",
            "total": {},
        },
    }

    # второй блок ДОХОД-РАСХОД
    arr_in_out_after_all_ip = {
        "name": None,
        "category": [
            {
                "name": "ПРОВЕРКА ДОХОД - РАСХОД",
                "total": {},
            },
            {
                "name": "ДОХОД-РАСХОД+отложенные налоги",
                "total": {},
            },
            {
                "name": "ФАКТИЧЕСКАЯ ОПЛАТА НАЛОГОВ",
                "total": {},
            },
        ],
    }
    # Процентные суммы на премию и перевод

    arr_summ_to_persent_ip = {
        "name": None,
        "category": [
            {
                "name": "на квартальную премию собственникам",
                "total": {},
            },
            {
                "name": "компенсация владельцу с ИП",
                "total": {},
            },
        ],
    }
    # хранилище
    arr_keep_ip = {
        "name": "В ХРАНИЛИЩЕ:",
        "category": [
            {
                "name": "остаток ПРИБЫЛЬ 1% ЦРП 5%",
                "total": {},
            },
            {
                "name": "остаток КВ 0,5 % ЦРП 50%",
                "total": {},
            },
            {
                "name": "вывод остатков ООО в Хранилище",
                "total": {},
            },
        ],
        "total_category": {
            "name": "ИТОГО В ХРАНИЛИЩЕ из $:",
            "total": {},
        },
    }
    # Р/С на конец месяца
    arr_end_month_ip = {
        "name": "на конец месяца",
        "total": {},
    }
    
    
    
    
    
    arr_start_month_ip_old = copy.deepcopy(arr_start_month_ip)
    arr_in_ip_old = copy.deepcopy(arr_in_ip)
    arr_out_ip_old = copy.deepcopy(arr_out_ip)
    arr_in_out_all_ip_old = copy.deepcopy(arr_in_out_all_ip)
    arr_real_diff_ip_old = copy.deepcopy(arr_real_diff_ip)
    arr_inside_all_ip_old = copy.deepcopy(arr_inside_all_ip)
    arr_in_out_after_all_ip_old = copy.deepcopy(arr_in_out_after_all_ip)
    arr_summ_to_persent_ip_old = copy.deepcopy(arr_summ_to_persent_ip)
    arr_keep_ip_old = copy.deepcopy(arr_keep_ip)
    arr_end_month_ip_old = copy.deepcopy(arr_end_month_ip)
   
    old_oper_arr = {}

    
    
    
    
    
    
    
    
    
    
    cache_key = f"bank_{1}_context_{year_now}"
    context_ooo = cache.get(cache_key)
    context_ooo = cache.get(cache_key)

    # cache_key = f"bank_{1}_context_{year_now}"
    # context_ooo = cache.get(cache_key)
    old_oper_arr = fill_operations_arrays_ip(
            categ_percent_by_name,
            categ_percent_list,
            services,
            other_categ_subkontract,
            arr_start_month_ip_old,
            arr_inside_all_ip_old,
            arr_out_ip_old,
            arr_in_out_all_ip_old,
            arr_in_ip_old,
            arr_in_out_after_all_ip_old,
            arr_summ_to_persent_ip_old,
            arr_keep_ip_old,
            arr_end_month_ip_old,
            CATEGORY_OPERACCOUNT,
            months_current_year,
            month_numbers,
            year_now,
            operations_old,
            bank,
            arr_real_diff_ip_old,
            context_ooo,
            cate_oper_beetwen_by_name,
            categoru_nalog,
            is_old_oper=True,
            old_oper_arr=None
        )
    print(old_oper_arr)

    arr_start_month, arr_in, arr_out, arr_in_out_all, arr_real_diff,arr_inside_all,arr_in_out_after_all,arr_summ_to_persent,arr_keep_ip,arr_end_month_ip = (
        fill_operations_arrays_ip(
            categ_percent_by_name,
            categ_percent_list,
            services,
            other_categ_subkontract,
            arr_start_month_ip,
            arr_inside_all_ip,
            arr_out_ip,
            arr_in_out_all_ip,
            arr_in_ip,
            arr_in_out_after_all_ip,
            arr_summ_to_persent_ip,
            arr_keep_ip,
            arr_end_month_ip,
            CATEGORY_OPERACCOUNT,
            months_current_year,
            month_numbers,
            year_now,
            operations,
            bank,
            arr_real_diff_ip,
            context_ooo,
            cate_oper_beetwen_by_name,
            categoru_nalog,
            is_old_oper=False,
            old_oper_arr=old_oper_arr
        )
    )
    print(old_oper_arr,"3")
    context = {
        "title": title,
        "type_url": type_url,
        "bank": bank.id,
        "year_now":year_now,
        "months_current_year": months_current_year,
        "arr_in": arr_in,
        "arr_out": arr_out,
        "arr_real_diff": arr_real_diff,
        "arr_in_out_all": arr_in_out_all,
        "arr_inside_all": arr_inside_all,
        "arr_in_out_after_all": arr_in_out_after_all,
        "arr_summ_to_persent": arr_summ_to_persent,
        "arr_keep": arr_keep_ip,
        "arr_end_month": arr_end_month_ip,
        "arr_start_month": arr_start_month,
        "old_oper_arr": old_oper_arr,
    }
    return render(request, "bank/outside/outside_ip.html", context)


def outside_nal(request):
    locale.setlocale(locale.LC_ALL, "")
    title = "$"
    type_url = "outside"
    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month

    # Получаем только нужный банк
    bank = Bank.objects.get(id=3)
    operations = (
        Operation.objects.select_related(
            "bank_in",
            "bank_to",
            "operaccount",
            "salary",
            "nalog",
            "employee",
            "monthly_bill",
            "monthly_bill__service",
            "suborder",
            "suborder__month_bill",
            "suborder__month_bill__service",
            "suborder__platform",
            "suborder__category_employee",
            "suborder_other",
            "between_bank",
        )
        .filter(
            Q(bank_in=bank) | Q(bank_to=bank),
            data__year__gte=year_now,
        )
        .order_by("data")
    )

    # Создаем список месяцев текущего года
    months_current_year = [MONTHS_RU[month - 1] for month in range(1, month_now + 1)]
    months_current_year.reverse()

    # Создаем словарь для сопоставления названий месяцев с их номерами
    month_numbers = {month: i + 1 for i, month in enumerate(months_current_year)}

    services = Service.objects.all()

    # СТАРТОВЫЕ МАССИВЫ
    # ПОСТУПЛЕНИЯ
    arr_in = {
        "name": "ПОСТУПЛЕНИЯ",
        "category": [
            {
                "name": "по договорам услуг",
                "group": {},
            },
            {
                "name": "между счетами:",
                "group": {
                    "взято из остатков": {},
                },
            },
        ],
        "total_category": {
            "name": "ИТОГО ПОСТУПЛЕНИЯ",
            "total": {},
        },
    }
    # СУБПОДРЯДЧИКИ + ПЛОЩАДКИ, в т.ч.
    arr_out = {
        "name": "СУБПОДРЯДЧИКИ + ПЛОЩАДКИ, в т.ч.",
        "category": [
            {
                "name": "по договорам услуг",
                "group": {},
            },
            {
                "name": "между счетами:",
                "group": {
                    "зачисление на ИП для оплаты субподряда": {},
                    "откладываем в хранилище на будущие расходы": {},
                },
            },
        ],
        "total_category": {
            "name": "ИТОГО СУБПОДРЯДЧИКИ + ПЛОЩАДКИ",
            "total": {},
        },
    }
    # петвый блок ДОХОД-РАСХОД
    arr_in_out_all = {
        "name": None,
        "category": [
            {
                "name": "РЕАЛЬНЫЕ ПОСТУПЛЕНИЯ ООО (ВЫРУЧКА-СУБПОДРЯД И БУХ)",
                "total": {},
            },
            {
                "name": "ПРИБЫЛЬ 1% ЦРП 5%",
                "total": {},
            },
            {
                "name": "КВ 20% ЦРП 50%",
                "total": {},
            },
            {
                "name": "ПРЕМИИ",
                "total": {},
            },
        ],
    }
    # ПРОВЕРКА ОБЩИЙ ДОХОД - РАСХОД - КВ И ТД
    arr_real_diff = {
        "name": "ПРОВЕРКА ОБЩИЙ ДОХОД - РАСХОД - КВ И ТД",
        "total": {},
    }
    # ВНУТРЕННИЕ СЧЕТА
    arr_inside_all = {
        "name": "ВНУТРЕННИЕ СЧЕТА",
        "category": [
            {
                "name": "ЗП $",
                "total": {
                    "name": "ЗП $",
                    "total": {},
                },
            },
            {
                "name": "ОПЕР СЧЕТ, в т.ч.:",
                "group": {},
                "total": {
                    "name": "ИТОГО ОПЕР СЧЁТ",
                    "total": {},
                },
            },
        ],
        "total_category": {
            "name": "ИТОГО РАСХОДЫ ВНУТРЕННИЕ СЧЕТА",
            "total": {},
        },
    }
    arr_summ_to_persent = {
        "name": None,
        "category": [
            {
                "name": "на квартальную премию собственникам",
                "total": {},
            },
            {
                "name": "компенсация владельцу с ИП",
                "total": {},
            },
        ],
    }
    # хранилище
    arr_keep = {
        "name": "В ХРАНИЛИЩЕ:",
        "category": [
            {
                "name": "остаток $",
                "total": {},
            },
            {
                "name": "остаток ПРИБЫЛЬ 1% ЦРП 5%",
                "total": {},
            },
            {
                "name": "остаток КВ 0,5 % ЦРП 50%",
                "total": {},
            },
            {
                "name": "отложенные в хранилище на будущие расходы",
                "total": {},
            },
        ],
        "total_category": {
            "name": "ИТОГО В ХРАНИЛИЩЕ из $:",
            "total": {},
        },
    }

    # Добавляем месяцы
    for i, month in enumerate(months_current_year):
        month_number = month_numbers[month]
        # Для итогов поступления
        arr_in["total_category"]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
            "is_make_operations": False,
        }
        arr_out["total_category"]["total"][month] = {
            "amount_month": 0,
            "month_number": f"{month_number:02d}",
            "is_make_operations": False,
        }
        # arr_out["category"][0]["group"][name] = {}
        # arr_out["category"][0]["group"][name][month] = {
        #             "amount_month": 0,
        #             "month_number": MONTHS_RU.index(month) + 1,
        #             "is_make_operations": False,
        #         }
    # Добавляем месяцы по сервисам
    for service in services:
        name = f"{service.name}({service.name_long_ru})"
        arr_in["category"][0]["group"][name] = {}
        arr_out["category"][0]["group"][name] = {}
        for i, month in enumerate(months_current_year):

            # Для услуг
            month_number = month_numbers[month]
            arr_in["category"][0]["group"][name][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
                "is_make_operations": False,
            }

            arr_out["category"][0]["group"][name][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
                "is_make_operations": False,
            }

    # распределение операций
    for operation in operations:
        month_name = MONTHS_RU[operation.data.month - 1]
        prev_month = MONTHS_RU[operation.data.month]

        if operation.monthly_bill and operation.suborder is None:
            # поступления по договорам услуг

            service_name = f"{operation.monthly_bill.service.name}({operation.monthly_bill.service.name_long_ru})"

            if service_name in arr_in["category"][0]["group"]:
                arr_in["category"][0]["group"][service_name][month_name][
                    "amount_month"
                ] += operation.amount
                arr_in["total_category"]["total"][month_name][
                    "amount_month"
                ] += operation.amount

        # операции расхода по договорам услуг
        elif operation.suborder:
            service_name = f"{operation.suborder.month_bill.service.name}({operation.suborder.month_bill.service.name_long_ru})"
            if service_name in arr_out["category"][0]["group"]:
                arr_out["category"][0]["group"][service_name][month_name][
                    "amount_month"
                ] += operation.amount
                arr_out["category"][0]["group"][service_name][month_name][
                    "operation_id"
                ] = operation.id
            # Добавляем в общий итог по месяцу операции
            arr_out["total_category"]["total"][month_name][
                "amount_month"
            ] += operation.amount

    context = {
        "title": title,
        "year_now": year_now,
        "type_url": type_url,
        "bank": bank.id,
        "months_current_year": months_current_year,
        "arr_in": arr_in,
        "arr_out": arr_out,
        "arr_in_out_all": arr_in_out_all,
        "arr_real_diff": arr_real_diff,
        "arr_inside_all": arr_inside_all,
        "arr_summ_to_persent": arr_summ_to_persent,
        "arr_keep": arr_keep,
    }
    return render(request, "bank/outside/outside_nal.html", context)


# ХРАНИЛИЩЕ
def storage(request):
    locale.setlocale(locale.LC_ALL, "")
    title = "Хранилище"
    type_url = "storage"
    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month
    # Получаем только нужный банк
    bank = Bank.objects.get(id=4)
    operations = (
        Operation.objects.select_related(
            "bank_in",
            "bank_to",
            "operaccount",
            "salary",
            "nalog",
            "employee",
            "monthly_bill",
            "monthly_bill__service",
            "suborder",
            "suborder__month_bill",
            "suborder__month_bill__service",
            "suborder__platform",
            "suborder__category_employee",
            "suborder_other",
            "between_bank",
        )
        .filter(
            Q(bank_in=bank) | Q(bank_to=bank),
            data__year__gte=year_now,
        )
        .order_by("data")
    )

    # Создаем список месяцев текущего года
    months_current_year = [MONTHS_RU[month - 1] for month in range(1, month_now + 1)]
    months_current_year.reverse()
    # Создаем словарь для сопоставления названий месяцев с их номерами
    month_numbers = {month: i + 1 for i, month in enumerate(months_current_year)}

    # СТАРТОВЫЕ МАССИВЫ

    # НАКОПИТЕЛЬНЫЕ СЧЕТА И НАЛИЧНЫЕ
    # ПОСТУПЛЕНИЯ
    arr_in = {
        "name": "Поступления:",
        "category": [
            {
                "name": "$",
                "total": {},
            },
            {
                "name": "ИП",
                "total": {},
            },
            {
                "name": "из остатков рекламных бюджетов",
                "total": {},
            },
            {
                "name": "возврат долга",
                "total": {},
            },
            {
                "name": "прочие возвраты",
                "total": {},
            },
        ],
        "total_category": {
            "name": "ИТОГО поступления",
            "total": {},
        },
    }
    # Расход:
    arr_out = {
        "name": "Поступления:",
        "category": [
            {
                "name": "перевод на вклад",
                "total": {},
            },
            {
                "name": "в долг",
                "total": {},
            },
            {
                "name": "покупки/траты",
                "total": {},
            },
            {
                "name": "зачисление на ООО",
                "total": {},
            },
            {
                "name": "зачисление на ИП",
                "total": {},
            },
        ],
        "total_category": {
            "name": "ИТОГО Расход",
            "total": {},
        },
    }

    # ПРЕМИИ
    #  на квартальные премии 1:
    arr_bonus_1 = {
        "name": "на квартальные премии 1:",
        "category": [
            {
                "name": "с $",
                "total": {},
            },
            {
                "name": "с ООО -> ИП",
                "total": {},
            },
        ],
        # "total_category": {
        #     "name": "ИТОГО поступления",
        #     "total": {},
        # },
    }
    # на квартальные премии 2:
    arr_bonus_2 = {
        "name": "на квартальные премии 2:",
        "category": [
            {
                "name": "с $",
                "total": {},
            },
            {
                "name": "с ООО -> ИП",
                "total": {},
            },
        ],
        # "total_category": {
        #     "name": "ИТОГО поступления",
        #     "total": {},
        # },
    }

    # ОСТАТКИ БЮДЖЕТОВ НА БУДУЩИЕ РАСХОДЫ
    arr_service = {
        "name": "Поступления:",
        "category": [
            {
                "name": "$",
                "total": {},
            },
        ],
    }

    context = {
        "title": title,
        "year_now": year_now,
        "type_url": type_url,
        "months_current_year": months_current_year,
        "bank": bank.id,
        "arr_service": arr_service,
        "arr_bonus_2": arr_bonus_2,
        "arr_bonus_1": arr_bonus_1,
        "arr_out": arr_out,
        "arr_in": arr_in,
    }

    return render(request, "bank/outside/storage.html", context)


def storage_all(request):
    title = "Хранилище"
    type_url = "storage"
    context = {
        "title": title,
        "type_url": type_url,
    }

    return render(request, "bank/storage/storage_all.html", context)


def storage_banking(request):
    title = "Накопительные счета"
    type_url = "storage_banking"
    context = {
        "title": title,
        "type_url": type_url,
    }

    return render(request, "bank/storage/storage_banking.html", context)


def storage_bonus(request):
    title = "Премии"
    type_url = "storage_bonus"
    context = {
        "title": title,
        "type_url": type_url,
    }

    return render(request, "bank/storage/storage_bonus.html", context)


def storage_servise(request):
    title = "Остатки рекламных бюджетов"

    type_url = "storage_servise"
    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month

    # Получаем только нужный банк
    bank = Bank.objects.get(id=4)

    # Создаем список месяцев текущего года
    months_current_year = [MONTHS_RU[month - 1] for month in range(1, month_now + 1)]
    months_current_year.reverse()
    # Создаем словарь для сопоставления названий месяцев с их номерами
    month_numbers = {month: i + 1 for i, month in enumerate(months_current_year)}

    operations = (
        Operation.objects.select_related(
            "bank_in",
            "bank_to",
            "operaccount",
            "salary",
            "nalog",
            "employee",
            "monthly_bill",
            "monthly_bill__service",
            "suborder",
            "suborder__month_bill",
            "suborder__month_bill__service",
            "suborder__platform",
            "suborder__category_employee",
            "suborder_other",
            "between_bank",
        )
        .filter(
            Q(bank_in=bank) | Q(bank_to=bank),
            data__year__gte=year_now,
        )
        .order_by("data")
    )

    # ОСТАТКИ БЮДЖЕТОВ НА БУДУЩИЕ РАСХОДЫ
    arr_service = {
        "name": "Поступления:",
        "category": [
            {
                "name": "Поступления",
                "total": {},
            },
        ],
    }

    # ЗАПОЛНЕНИЕ МАССИВОВ ДАННЫМИ

    for i, month in enumerate(months_current_year):
        month_number = month_numbers[month]

        arr_service["category"][0]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
        }

    # распределение операций
    for operation in operations:
        month_name = MONTHS_RU[operation.data.month - 1]

        if operation.monthly_bill and operation.suborder is None:
            # поступления по договорам услуг
            arr_service["category"][0]["total"][month_name][
                "amount_month"
            ] += operation.amount

    context = {
        "title": title,
        "type_url": type_url,
        "title": title,
        "year_now": year_now,
        "type_url": type_url,
        "bank": bank.id,
        "arr_service": arr_service,
        "months_current_year": months_current_year,
    }

    return render(request, "bank/storage/storage_servise.html", context)
