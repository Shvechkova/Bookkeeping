import datetime
import pymorphy3
import itertools
from django.shortcuts import render
from django.db.models.functions import TruncMonth
from django.db.models import Prefetch, OuterRef
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q, F, OrderBy, Case, When, Value
from apps.bank.models import CATEGORY_OPERACCOUNT, GroupeOperaccount
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
    
    # Получаем операции
    operations = (
        Operation.objects.filter(operaccount__isnull=False, data__year__gte=year_now)
        .select_related("operaccount")
        .prefetch_related()
        .order_by("-data")
    )
    print(operations)
    category = CATEGORY_OPERACCOUNT
    groupeis = GroupeOperaccount.objects.all()
    
    # Создаем морфологический анализатор
    morph = pymorphy3.MorphAnalyzer(lang="ru")
    
    # Создаем структуру для хранения данных по категориям и счетам
    operations_by_category = {}
    for cat in CATEGORY_OPERACCOUNT:
        cat_id = cat[0]
        operations_by_category[cat_id] = {
            'name': cat[1],  # Название категории
            'accounts': {}   # Словарь для счетов
        }
        
    # Получаем все счета одним запросом
    all_accounts = GroupeOperaccount.objects.all()
    
    # Создаем список месяцев текущего года
    months_current_year = []
    for month in range(1, month_now + 1):
        month_name = MONTHS_RU[month - 1]
        months_current_year.append(month_name)
    months_current_year.reverse()
    print(months_current_year)
    
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
            cat_data['accounts'][account.name] = {
                'account': account,
                'months': {}
            }
            # Инициализируем месяцы для каждого счета
            for month in months_current_year:
                cat_data['accounts'][account.name]['months'][month] = {
                    'operations': [],
                    'total': 0
                }
    
    print(cat_data)
    
    # Группируем операции
    for operation in operations:
        print(operation)
        month_name = morph.parse(operation.data.strftime("%B"))[0].normal_form.title()
        print(month_name)
        account = operation.operaccount
        category_id = account.category
        
        if category_id in operations_by_category:
            account_name = account.name
            if account_name in operations_by_category[category_id]['accounts']:
                if month_name in operations_by_category[category_id]['accounts'][account_name]['months']:
                    # Добавляем операцию
                    operations_by_category[category_id]['accounts'][account_name]['months'][month_name]['operations'].append(operation)
                    operations_by_category[category_id]['accounts'][account_name]['months'][month_name]['total'] += operation.amount
    
    # Преобразуем в список для шаблона
    operations_arr = []
    for cat_id, cat_data in operations_by_category.items():
        category_info = {
            'category_id': cat_id,
            'category_name': cat_data['name'],
            'accounts': []
        }
        
        # Добавляем данные по счетам
        for account_name, account_data in cat_data['accounts'].items():
            account_info = {
                'name': account_name,
                'account': account_data['account'],
                'months': []
            }
            
            # Добавляем данные по месяцам
            for i, month_name in enumerate(months_current_year):
                month_data = account_data['months'][month_name]
                month_info = {
                    'month': month_name,
                    'operations': month_data['operations'],
                    'total': month_data['total'],
                     'budget': 0  # Инициализируем бюджет
                }
                if i < len(months_current_year) - 1:
                    prev_month = months_current_year[i + 1]
                    prev_month_total = account_data['months'][prev_month]['total']
                    month_info['budget'] = prev_month_total
                    
                account_info['months'].append(month_info)
            
            category_info['accounts'].append(account_info)
        
        operations_arr.append(category_info)
        
    for category_info in operations_arr:
        totals_by_month = []
        for i, month_name in enumerate(months_current_year):
            total = 0
            for account in category_info['accounts']:
                total += account['months'][i]['total']
            totals_by_month.append(total)
        category_info['totals_by_month'] = totals_by_month
        
    print(operations_arr)
    context = {
        "title": title,
        "type_url": type_url,
        "operations": operations_arr,
        "groupeis": groupeis,
        "category": category,
        "months": months_current_year,
    }
    
    return render(request, "bank/inside/inside_one_oper_accaunt.html", context)


def salary(request):
    title = "salary"
    type_url = "inside"

    data = datetime.datetime.now()
    year_now = datetime.datetime.now().year
    month_now = datetime.datetime.now().month
    date_start_year = str(year_now) + "-01-01"

    employee_now_year = Employee.objects.filter(
        date_end__isnull=True, date_end__gte=date_start_year
    )

    context = {
        "title": title,
        "type_url": type_url,
    }

    return render(request, "bank/inside/inside_one_salary.html", context)
