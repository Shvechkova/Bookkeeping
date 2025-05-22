import datetime
import pymorphy3
import itertools
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.db.models.functions import TruncMonth
from django.db.models import Prefetch, OuterRef
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q, F, OrderBy, Case, When, Value
from apps.bank.models import CATEGORY_OPERACCOUNT, GroupeOperaccount, GroupeSalary
from apps.employee.models import Employee
from apps.operation.models import Operation
from project.settings import MONTHS_RU


# Create your views here.
def storage(request):
    title = "Хранилище"
    context = {
        "title": title,
    }

    return render(request, "bank/storage.html", context)


def inside(request):
    title = "Внутренние счета"
    type_url = "inside"
    context = {
        "title": title,
        "type_url": type_url,
    }

    return render(request, "bank/inside/inside_all.html", context)


def oper_accaunt(request):
    import locale

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
                        ]["months"][month_name] = {"operations": [], "total": 0,"comment": False,}

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
                        
                        operations_old_by_year[year]["categories"][category_id][
                    "accounts"
                ][account_name]["months"][month_name]
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
                        "comment":  month_data["comment"], 
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
                    "comment":  month_data["comment"], 
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
    month_now = datetime.datetime.now().month
    date_start_year = str(year_now) + "-01-01"
    
    month_now_name = MONTHS_RU[month_now - 1]

    # Получаем активных сотрудников
    employee_now_year = Employee.objects.filter(
        # date_end__gte=date_start_year
    )
   

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
        .select_related("salary")
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
                print(category)
                # Сумма по всем месяцам для этого сотрудника и категории
                cat_total = sum(
                    value for key, value in categories_by_month.get(category, {}).items() 
                    if key not in ['prev_month_values', 'total']
                )
     
                # bank_in = cat.bank.id
                bank_in = None
                for k, v in salary_groups_bank.items():
                   
                    if k == category:
                        bank_in = v
                        
                cat_in = None
                for k, v in cat_name_id.items():
                   
                    if k == category:
                        cat_in = v
                        
                        
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
    }
    print(context)

    return render(request, "bank/inside/inside_one_salary.html", context)
