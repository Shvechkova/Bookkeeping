import datetime
import pymorphy3
import itertools
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.db.models.functions import TruncMonth
from django.db.models import Prefetch, OuterRef
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q, F, OrderBy, Case, When, Value
from apps.bank.models import CATEGORY_OPERACCOUNT, Bank, CategNalog, GroupeOperaccount, GroupeSalary
from apps.employee.models import Employee
from apps.operation.models import Operation
from apps.service.models import Service
from project.settings import MONTHS_RU
import locale


# Create your views here.


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
    print(operations_by_category)
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

    # Преобразуем в список для шаблона
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
            q_object &= Q( date_end__isnull=True)
            q_object |= Q(date_end__year=year_now_st )
        else:
            q_object &= Q(date_end__year__lte=year_now_st)
    else:
        q_object &= Q(date_end__isnull=True)
        q_object |= Q(date_end__year=year_now_st )
        
    print(q_object)
    # Получаем активных сотрудников
    employee_now_year = Employee.objects.filter(q_object)

    # Создаем морфологический анализатор
    morph = pymorphy3.MorphAnalyzer(lang="ru")

    # Создаем список месяцев текущего года в обратном порядке
    months_current_year = []
    for month in range(1, month_now + 1):
        month_name = MONTHS_RU[month - 1]
        months_current_year.append(month_name)
        
    months_current_year.reverse()
    months_current_year_2 = months_current_year.copy()
    all_categories_qs = GroupeSalary.objects.all().select_related("bank").prefetch_related(Prefetch("bank"))
    all_categories_bank = all_categories_qs.values_list("bank","name","id")
    print(all_categories_bank)
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
                    # Для Оф ЗП (10 число) добавляем в итог следующего месяца
                    next_month_index = months_current_year.index(month_name) - 1
                    if next_month_index >= 0:
                        next_month = months_current_year[next_month_index]
                        employees_data[employee_id]["months"][next_month][
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
        if category not in operations_old_by_year[year]["employees"][employee_id]["categories_by_month"]:
            operations_old_by_year[year]["employees"][employee_id]["categories_by_month"][category] = {}
            operations_old_by_year[year]["employees"][employee_id]["operations_by_month"][category] = {}

        # Добавляем операцию
        operations_old_by_year[year]["employees"][employee_id]["categories_by_month"][category][month_name] = operation.amount
        operations_old_by_year[year]["employees"][employee_id]["operations_by_month"][category][month_name] = operation.id

        # Обновляем total_by_month
        month_idx = MONTHS_RU.index(month_name)
        if category == "Оф ЗП (10 число)":
            # Для "Оф ЗП (10 число)" добавляем в следующий месяц
            if month_idx < len(MONTHS_RU) - 1:
                operations_old_by_year[year]["employees"][employee_id]["total_by_month"][month_idx + 1] += operation.amount
        else:
            operations_old_by_year[year]["employees"][employee_id]["total_by_month"][month_idx] += operation.amount

    # Формируем groups_full для старых операций
    for year_data in operations_old_by_year.values():
        for employee_data in year_data["employees"].values():
            # Добавляем общую сумму для сотрудника
            employee_total = 0
            employee_data["groups_full"] = []
            
            # Считаем общие тоталы за год для долгов
            total_debt_issued = sum(
                value for key, value in employee_data["categories_by_month"].get("Выдано в долг", {}).items()
                if key not in ['prev_month_values', 'total']
            )
            total_debt_returned = sum(
                value for key, value in employee_data["categories_by_month"].get("Возврат долга", {}).items()
                if key not in ['prev_month_values', 'total']
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
                            group_info["totals_by_month"][month_idx] = total_debt_balance
                    else:
                        cat_total = sum(
                            value for key, value in employee_data["categories_by_month"].get(category, {}).items()
                            if key not in ['prev_month_values', 'total']
                        )
                    bank_in = salary_groups_bank.get(category)
                    cat_in = cat_name_id.get(category)

                    group_info["categories"].append({
                        "name": category,
                        "name_id": cat_in,
                        "amount": cat_total,
                        "bank_in": bank_in,
                        "total_year": cat_total,
                    })

                    # Обновляем totals_by_month для группы
                    for month_idx, month in enumerate(MONTHS_RU):
                        if category == "Оф ЗП (10 число)":
                            # Для "Оф ЗП (10 число)" берем значение из предыдущего месяца
                            if month_idx > 0:
                                prev_month = MONTHS_RU[month_idx - 1]
                                amount = employee_data["categories_by_month"].get(category, {}).get(prev_month, 0)
                                group_info["totals_by_month"][month_idx] += amount
                                # Добавляем в общий тотал по месяцам
                                if group_name != "group4":
                                    employee_data["total_by_month"][month_idx] += amount
                        elif group_name == "group4":
                            # Для группы 4 (долги) используем общий баланс за год
                            group_info["totals_by_month"][month_idx] = total_debt_balance
                        else:
                            amount = employee_data["categories_by_month"].get(category, {}).get(month, 0)
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
                employee["months"].append({
                    "name": month,
                    "date_start": date_start,
                })
                
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
            }
        }

        # Словарь для хранения остатков долга по всем сотрудникам
        total_debt_balances = {}
        
        # Считаем общие тоталы за год для долгов
        total_debt_issued = 0
        total_debt_returned = 0
        
        for employee in year_data["employees"]:
            # Суммируем выданные долги
            total_debt_issued += sum(
                value for key, value in employee.get("categories_by_month", {}).get("Выдано в долг", {}).items()
                if key not in ['prev_month_values', 'total']
            )
            # Суммируем возвращенные долги
            total_debt_returned += sum(
                value for key, value in employee.get("categories_by_month", {}).get("Возврат долга", {}).items()
                if key not in ['prev_month_values', 'total']
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
                total_debt_issued += employee.get("categories_by_month", {}).get("Выдано в долг", {}).get(month, 0)
                total_debt_returned += employee.get("categories_by_month", {}).get("Возврат долга", {}).get(month, 0)
            
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
                                if month_idx > 0:
                                    prev_month = MONTHS_RU[month_idx - 1]
                                    amount = employee.get("categories_by_month", {}).get(category["name"], {}).get(prev_month, 0)
                                    totals_old_by_month[year]["ИТОГО ЗП с ООО"][month_idx] += amount
                                    totals_old_by_month[year]["total_year"]["ИТОГО ЗП с ООО"] += amount
                            else:
                                amount = employee.get("categories_by_month", {}).get(category["name"], {}).get(month, 0)
                                totals_old_by_month[year]["ИТОГО ЗП с ООО"][month_idx] += amount
                                totals_old_by_month[year]["total_year"]["ИТОГО ЗП с ООО"] += amount
                elif group["name"] == "group2":
                    # Для group2 ($) суммируем все категории
                    for month_idx, total in enumerate(group["totals_by_month"]):
                        totals_old_by_month[year]["ИТОГО ЗП с $"][month_idx] += total
                    # Добавляем в общий тотал за год
                    totals_old_by_month[year]["total_year"]["ИТОГО ЗП с $"] += group["total_year"]
                elif group["name"] == "group3":
                    # Для group3 (КВ) распределяем по соответствующим категориям
                    for category in group["categories"]:
                        for month_idx, month in enumerate(MONTHS_RU):
                            amount = employee.get("categories_by_month", {}).get(category["name"], {}).get(month, 0)
                            if category["name"] == "КВ $":
                                totals_old_by_month[year]["ИТОГО КВ $"][month_idx] += amount
                                totals_old_by_month[year]["total_year"]["ИТОГО КВ $"] += amount
                            elif category["name"] == "КВ ИП":
                                totals_old_by_month[year]["ИТОГО КВ ИП"][month_idx] += amount
                                totals_old_by_month[year]["total_year"]["ИТОГО КВ ИП"] += amount
                            elif category["name"] == "квартальная премия":
                                totals_old_by_month[year]["ИТОГО кварт. премия"][month_idx] += amount
                                totals_old_by_month[year]["total_year"]["ИТОГО кварт. премия"] += amount
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
                        if idx > 0:
                            next_month = months_current_year[idx - 1]
                            # Добавляем в total следующего месяца
                            if "total" not in categories_by_month[op_category]:
                                categories_by_month[op_category]["total"] = {}
                            categories_by_month[op_category]["total"][next_month] = op.amount

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
                    if idx < len(months_current_year) - 1:
                        next_month = months_current_year[idx + 1]
                        if next_month in categories_by_month[category]:
                            if "total" not in categories_by_month[category]:
                                categories_by_month[category]["total"] = {}
                            categories_by_month[category]["total"][month] = categories_by_month[category][next_month]

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
                    value for key, value in categories_by_month.get(category, {}).items() 
                    if key not in ['prev_month_values', 'total']
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
            debt_issued = employee_info["categories_by_month"].get("Выдано в долг", {}).get(month, 0)
            debt_returned = employee_info["categories_by_month"].get("Возврат долга", {}).get(month, 0)
            
            # Рассчитываем текущий остаток
            current_balance = prev_balance + debt_issued - debt_returned
            current_balance = max(0, current_balance)  # Не даем остатку уйти в минус
            
            # Сохраняем остаток в промежуточный словарь
            debt_balances[month] = current_balance
            
            # Сохраняем остаток в categories_by_month
            if "Остаток долга" not in employee_info["categories_by_month"]:
                employee_info["categories_by_month"]["Остаток долга"] = {}
            employee_info["categories_by_month"]["Остаток долга"][month] = current_balance
        
        # Теперь рассчитываем общие суммы по месяцам в правильном порядке
        for month in months_current_year:
            month_total = 0
            for group in employee_info["groups_full"]:
                if group["name"] != "group4":
                    for cat in group["categories"]:
                        if cat["name"] == "Оф ЗП (10 число)":
                            # Для "Оф ЗП (10 число)" берем значение из следующего месяца
                            idx = months_current_year.index(month)
                            if idx < len(months_current_year) - 1:  # Если это не последний месяц
                                next_month = months_current_year[idx + 1]
                                month_total += employee_info["categories_by_month"].get(cat["name"], {}).get(next_month, 0)
                        else:
                            month_total += employee_info["categories_by_month"].get(cat["name"], {}).get(month, 0)
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
                month_total = 0
                if group["name"] == "group4":
                    # Для группы 4 берем остаток долга
                    month_total = employee_info["categories_by_month"].get("Остаток долга", {}).get(month, 0)
                else:
                    for cat in group["categories"]:
                        if cat["name"] == "Оф ЗП (10 число)":
                            # Для "Оф ЗП (10 число)" берем значение из следующего месяца
                            idx = months_current_year.index(month)
                            if idx < len(months_current_year) - 1:
                                next_month = months_current_year[idx + 1]
                                month_total += employee_info["categories_by_month"].get(cat["name"], {}).get(next_month, 0)
                        else:
                            month_total += employee_info["categories_by_month"].get(cat["name"], {}).get(month, 0)
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

    for idx, month in enumerate(months_current_year):
        for employee in employees_list:
            # Итоги по ООО (group1)
            for category in employee["categories_by_month"]:
                if category == "Оф ЗП (10 число)":
                    # Для "Оф ЗП (10 число)" берем значение из следующего месяца
                    if idx < len(months_current_year) - 1:
                        next_month = months_current_year[idx + 1]
                        totals_by_month["ИТОГО ЗП с ООО"][idx] += employee["categories_by_month"][category].get(next_month, 0)
                else:
                    totals_by_month["ИТОГО ЗП с ООО"][idx] += employee["categories_by_month"][category].get(month, 0)
            
            # Итоги по $ (group2)
            totals_by_month["ИТОГО ЗП с $"][idx] += employee["months"][idx]["group2_total"]
            
            # Итоги по КВ $ и КВ ИП (из group3)
            for category in employee["categories_by_month"]:
                if category == "КВ $":
                    totals_by_month["ИТОГО КВ $"][idx] += employee["categories_by_month"][category].get(month, 0)
                elif category == "КВ ИП":
                    totals_by_month["ИТОГО КВ ИП"][idx] += employee["categories_by_month"][category].get(month, 0)
                elif category == "квартальная премия":
                    totals_by_month["ИТОГО кварт. премия"][idx] += employee["categories_by_month"][category].get(month, 0)
            
            # Итоги по долгам (group4) - используем group_month_totals
            totals_by_month["Итого общий долг"][idx] += employee["group_month_totals"]["group4"][idx]

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
    locale.setlocale(locale.LC_ALL, "")
    # Создаем морфологический анализатор
    morph = pymorphy3.MorphAnalyzer(lang="ru")
    
    title = "Налоги"
    type_url = "inside"
    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month
    categoru_nalog = CategNalog.objects.all().select_related('bank_in')
    
    
    # Создаем список месяцев текущего года
    months_current_year = []
    for month in range(1, month_now + 1):
        month_name = MONTHS_RU[month - 1]
        months_current_year.append(month_name)
    months_current_year.reverse()
    
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
                }
            },
            "totals_month": {}  # Добавляем общий итог для ООО
        },
        "ИП": {
            "name": "ИП (откладываем до оплаты)",
            "name_full": "ИП",
            "full_year_total": 0,
            "category": [],
            "totals_month": {}
        }
    }

    # Инициализируем totals_month для каждого типа банка и секции
    for bank_type, bank_data in operations_by_category.items():
        if bank_type == "OOO":
            for section_name, section_data in bank_data["sections"].items():
                for i, month in enumerate(months_current_year):
                    section_data["totals_month"][month] = {
                        "total": 0,
                        "expected": 0,  # Добавляем поле для ожидаемых расходов
                        "month_number": len(months_current_year) - i,
                        "date_start": datetime.datetime(
                            year_now, len(months_current_year) - i, 1
                        ),
                        "operation_id":0,
                        
                    }
            # Инициализируем общий итог для ООО
            for i, month in enumerate(months_current_year):
                bank_data["totals_month"][month] = {
                    "total": 0,
                    "expected": 0  # Добавляем поле для ожидаемых расходов
                }
        else:
            for i, month in enumerate(months_current_year):
                bank_data["totals_month"][month] = {
                    "total": 0,
                    "expected": 0,  # Добавляем поле для ожидаемых расходов
                    "month_number": len(months_current_year) - i,
                    "date_start": datetime.datetime(
                        year_now, len(months_current_year) - i, 1
                    ),  
                }
    
    for cat in categoru_nalog:
        arr = {
            "cat_name": cat.name,
            "cat_id": cat.id,
            "cat_bank_in": cat.bank_in.id,
            "cat_bank_in_name": cat.bank_in.name,
            "months": {}, # Словарь для счетов
            "full_year_total": 0,
        }
        
        # Инициализируем месяцы для каждого счета
        for i, month in enumerate(months_current_year):
            arr["months"][month] = {
                "month_name": month,
                "month_data": "",
                "total": 0,
                "expected": 0,  # Добавляем поле для ожидаемых расходов
                "month_number": len(months_current_year) - i,
                "date_start": datetime.datetime(
                    year_now, len(months_current_year) - i, 1
                ),  
                "operation_id":0
            }
        
        if cat.bank_in.id == 1:  # ООО
            if cat.name != "налог на аренду офиса":
                operations_by_category["OOO"]["sections"]["Налоги с ЗП"]["category"].append(arr)
            else:
                operations_by_category["OOO"]["sections"]["Прочие налоги"]["category"].append(arr)
        elif cat.bank_in.id == 2:  # ИП
            operations_by_category["ИП"]["category"].append(arr)
    
    
    operations_by_category_old = operations_by_category.copy()
    operations = (
        Operation.objects.filter(
            nalog__isnull=False, data__year__gte=year_now,
        )
        .select_related("nalog","nalog__bank_in")
        .prefetch_related()
        .order_by("-data")
    )

    # Обрабатываем операции
    for operation in operations:
        if operation.nalog:
            month_name = MONTHS_RU[operation.data.month - 1]
            
            # Определяем тип банка и категорию
            bank_type = "OOO" if operation.nalog.bank_in.id == 1 else "ИП"
            
            if bank_type == "OOO":
                # Определяем секцию для ООО
                section = "Налоги с ЗП" if operation.nalog.name != "налог на аренду офиса" else "Прочие налоги"
                
                # Находим соответствующую категорию в структуре
                for category in operations_by_category[bank_type]["sections"][section]["category"]:
                    if category["cat_id"] == operation.nalog.id:
                        # Обновляем данные для месяца
                        category["months"][month_name]["month_data"] = operation
                        category["months"][month_name]["total"] = operation.amount
                        category["months"][month_name]["operation_id"] = operation.id
                        
                        # Обновляем общий итог для секции
                        operations_by_category[bank_type]["sections"][section]["totals_month"][month_name]["total"] += operation.amount
                        operations_by_category[bank_type]["sections"][section]["totals_month"][month_name]["operation_id"] = operation.id
                        
                        # Обновляем общий итог для ООО
                        operations_by_category[bank_type]["totals_month"][month_name]["total"] += operation.amount
                        
                        # Обновляем full_year_total для категории
                        category["full_year_total"] += operation.amount
                        break
            else:  # ИП
                # Находим соответствующую категорию в структуре
                for category in operations_by_category[bank_type]["category"]:
                    if category["cat_id"] == operation.nalog.id:
                        # Обновляем данные для месяца
                        category["months"][month_name]["month_data"] = operation
                        category["months"][month_name]["total"] = operation.amount
                        category["months"][month_name]["operation_id"] = operation.id
                        
                        # Обновляем общий итог для ИП
                        operations_by_category[bank_type]["totals_month"][month_name]["total"] += operation.amount
                        
                        # Обновляем full_year_total для категории
                        category["full_year_total"] += operation.amount
                        break

    # Рассчитываем ожидаемые расходы на основе предыдущего месяца
    for bank_type, bank_data in operations_by_category.items():
        if bank_type == "OOO":
            for section_name, section_data in bank_data["sections"].items():
                # Рассчитываем full_year_total для секции
                section_data["full_year_total"] = sum(
                    month_data["total"] for month_data in section_data["totals_month"].values()
                )
                
                for i, month in enumerate(months_current_year):
                    if i < len(months_current_year) - 1:  # Если это не последний месяц
                        prev_month = months_current_year[i + 1]
                        # Устанавливаем ожидаемые расходы равными сумме предыдущего месяца
                        section_data["totals_month"][month]["expected"] = section_data["totals_month"][prev_month]["total"]
                        
                        # Обновляем ожидаемые расходы для категорий
                        for category in section_data["category"]:
                            category["months"][month]["expected"] = category["months"][prev_month]["total"]
            
            # Обновляем общие ожидаемые расходы для ООО
            for i, month in enumerate(months_current_year):
                if i < len(months_current_year) - 1:
                    prev_month = months_current_year[i + 1]
                    bank_data["totals_month"][month]["expected"] = bank_data["totals_month"][prev_month]["total"]
            
            # Рассчитываем full_year_total для ООО
            bank_data["full_year_total"] = sum(
                month_data["total"] for month_data in bank_data["totals_month"].values()
            )
        else:  # ИП
            for i, month in enumerate(months_current_year):
                if i < len(months_current_year) - 1:
                    prev_month = months_current_year[i + 1]
                    bank_data["totals_month"][month]["expected"] = bank_data["totals_month"][prev_month]["total"]
                    
                    # Обновляем ожидаемые расходы для категорий ИП
                    for category in bank_data["category"]:
                        category["months"][month]["expected"] = category["months"][prev_month]["total"]
            
            # Рассчитываем full_year_total для ИП
            bank_data["full_year_total"] = sum(
                month_data["total"] for month_data in bank_data["totals_month"].values()
            )

    operations_old = (
        Operation.objects.filter(
             nalog__isnull=False, data__year__lt=year_now,
        )
        .select_related("nalog")
        .prefetch_related()
        .order_by("-data")
    )
    
    context = {
        "title": title,
        "type_url": type_url,
        "operations_by_category": operations_by_category,
        "year_now": year_now
    }
    
    return render(request, "bank/inside/inside_one_nalog.html", context)


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
    bank = Bank.objects.get(id=1)
    operations_in = (
        Operation.objects.filter(data__year__gte=year_now, bank_to=bank)
        .select_related()
        .prefetch_related()
        .order_by("-data")
    )

    operations_out = (
        Operation.objects.filter(data__year__gte=year_now, bank_in=bank)
        .select_related()
        .prefetch_related()
        .order_by("-data")
    )
    # Создаем список месяцев текущего года
    months_current_year = []
    for month in range(1, month_now + 1):
        month_name = MONTHS_RU[month - 1]
        months_current_year.append(month_name)
    months_current_year.reverse()

    print(months_current_year)

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
                },
            },
        ],
        "total_category": {
            "name": "ИТОГО ПОСТУПЛЕНИЯ",
            "total": {},
        },
    }
    arr_out = {
        "name": "СУБПОДРЯДЧИКИ + ПЛОЩАДКИ, в т.ч.",
        "category": [
            {
                "name": "по договорам услуг",
                "group": {
                    "SEO": {
                        "Topvisor": {},
                        "ИП Галаев": {},
                    },
                    "другое": {},
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
                "group": {
                    "бухгалтерия": {},
                },
            },
        ],
        "total_category": {
            "name": "ИТОГО СУБПОДРЯДЧИКИ + ПЛОЩАДКИ",
            "total": {},
        },
    }

    arr_operaccount = {
        "name": "ОПЕР СЧЕТ",
        "category": [],
        "total_category": {
            "name": "ИТОГО ОПЕР СЧЁТ",
            "total": {},
        },
    }

    # Добавляем категории из CATEGORY_OPERACCOUNT
    for categ_oper in CATEGORY_OPERACCOUNT:
        category_data = {
            "name": categ_oper[1],
            "group": {}
        }
        # Добавляем месяцы для каждой категории
        for month in months_current_year:
            category_data["group"][month] = {
                "amount_month": 0
            }
        arr_operaccount["category"].append(category_data)

    # Добавляем месяцы для итогов
    for month in months_current_year:
        arr_operaccount["total_category"]["total"][month] = {
            "amount_month": 0
        }

    services = Service.objects.all()

    for service in services:
        name = f"{service.name}({service.name_long_ru})"
        arr_in["category"][0]["group"][name] = {}

        for month in months_current_year:
            # Для услуг
            arr_in["category"][0]["group"][name][month] = {
                "amount_month": 0,
            }

            # Для переводов с ИП
            arr_in["category"][1]["group"]["перевод с ИП для оплаты субподряда"][
                month
            ] = {
                "amount_month": 0,
            }

            # Для переводов с $
            arr_in["category"][1]["group"]["перевод с $ для оплаты субподряда"][
                month
            ] = {
                "amount_month": 0,
            }

            # Для итогов
            arr_in["total_category"]["total"][month] = {
                "amount_month": 0,
            }

            # Для arr_out
            # Добавляем месяцы для SEO
            arr_out["category"][0]["group"]["SEO"]["Topvisor"][month] = {
                "amount_month": 0,
            }
            arr_out["category"][0]["group"]["SEO"]["ИП Галаев"][month] = {
                "amount_month": 0,
            }

            # Добавляем месяцы для переводов
            arr_out["category"][1]["group"]["перевод на ИП для оплаты субподряда"][
                month
            ] = {
                "amount_month": 0,
            }

            # Добавляем месяцы для бухгалтерии
            arr_out["category"][2]["group"]["бухгалтерия"][month] = {
                "amount_month": 0,
            }

            # Добавляем месяцы для итогов arr_out
            arr_out["total_category"]["total"][month] = {
                "amount_month": 0,
            }

    # Добавляем сервисы в "другое" для arr_out, исключая SEO
    for service in services:
        if service.name != "SEO":  # Пропускаем SEO
            name = f"{service.name}({service.name_long_ru})"
            arr_out["category"][0]["group"]["другое"][name] = {}
            for month in months_current_year:
                arr_out["category"][0]["group"]["другое"][name][month] = {
                    "amount_month": 0,
                }

    print(arr_in)

    context = {
        "title": title,
        "type_url": type_url,
        "operations_in": operations_in,
        "arr_in": arr_in,
        "arr_out": arr_out,
        "months_current_year": months_current_year,
        "arr_operaccount":arr_operaccount
    }
    return render(request, "bank/outside/outside_ooo.html", context)


def outside_ip(request):
    locale.setlocale(locale.LC_ALL, "")
    title = "ИП"
    type_url = "outside"
    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month

    context = {
        "title": title,
        "type_url": type_url,
    }
    return render(request, "bank/outside/outside_ip.html", context)


def outside_nal(request):
    locale.setlocale(locale.LC_ALL, "")
    title = "$"
    type_url = "outside"
    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month

    context = {
        "title": title,
        "type_url": type_url,
    }
    return render(request, "bank/outside/outside_nal.html", context)


def storage(request):
    title = "Хранилище"
    context = {
        "title": title,
    }

    return render(request, "bank/outside/storage.html", context)
