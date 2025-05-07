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


# def oper_accaunt(request):
#     # import locale
#     # locale.setlocale(locale.LC_ALL, "")
    
#     # title = "oper_accaunt"
#     # type_url = "inside"
#     # data = datetime.datetime.now()
#     # year_now = datetime.datetime.now().year
#     # month_now = datetime.datetime.now().month
#     # operations = (
#     #     Operation.objects.filter(operaccount__isnull=False, data__year__gte=year_now)
#     #     .select_related(
#     #         "operaccount",
#     #     )
#     #     .prefetch_related()
#     #     .order_by("-data")
#     # )
#     # print("operations", operations)
#     # operations_old = Operation.objects.filter(
#     #     operaccount__isnull=False, data__year__lte=year_now
#     # ).order_by("-data")

#     # category = CATEGORY_OPERACCOUNT
#     # groupeis = GroupeOperaccount.objects.all()
    
#     # import pymorphy3
#     # morph = pymorphy3.MorphAnalyzer(lang="ru")
#     # operations = itertools.groupby(
#     #     operations,
#     #     lambda t: [
#     #         morph.parse(t.data.strftime("%B"))[0].normal_form.title(),
#     #         t.operaccount,t.operaccount.category
#     #     ],
#     # )
#     # print(operations)
#     # # operations_arr = [
#     # #     (grouper, list(values)) for grouper, values in operations

#     # # ]
#     # # print("operations after account ", operations_arr)
#     # # актуальные месяца нынешнего года
#     # m = []
#     # month_names = []
#     # month_arr = []
#     # for month in range(1, month_now+1):
#     #     month_name = MONTHS_RU[month - 1]

#     #     month_names.append({
#     #         "name_month": month_name,
#     #         "month": month,
#     #     })
#     #     month_arr.append([month_name])
#     #     m.append(month_name)

#     # month_names.reverse()
#     # month_arr.reverse()
#     # m = str(m)
    
#     # groups = GroupeOperaccount.objects.all()
#     # print("groups",groups)
    
#     # month_cat_item = []
#     # month_cat_item2 = []
#     # for cat in CATEGORY_OPERACCOUNT:
#     #     gr_all = []
#     #     for group in  groups.filter(category=cat[0]):
#     #         gr = {group.name:[]}
#     #         gr = [group.name,[month_arr]]
#     #         gr_all.append(gr)
#     #     categ =  {cat[0]:gr_all}
#     #     categ_2 =[cat[0]]
#     #     print(categ_2)
#     #     categ_2.append(gr_all)
#     #     month_cat_item.append(categ)
#     #     month_cat_item2.append(categ_2)
    
#     # print(month_cat_item2)
    
#     # operations_arr = []
#     # for grouper, values in operations:
#     #     print(grouper)
#     #     total = ["total"]
#     #     val = list(values)
#     #     for v in val:
#     #         # print("v", v)
#     #         print(grouper[2])
#     #         arr = month_cat_item2[int(grouper[2] )-1 ]
            
#     #         print("arr",arr)
           
#     #     month_name = [f"{grouper[0]} {grouper[1]}"]
#     #     item = [month_name, val]
#     #     operations_arr.append(item)
#     #     operations_arr.append(total)
        
#     # print(operations_arr)
#     # context = {
#     #     "title": title,
#     #     "type_url": type_url,
#     #     "operations": month_cat_item2,
#     #     "groupeis": groupeis,
#     #     "category": category,
#     #     "month":m,
#     # }
#     return render(request, "bank/inside/inside_one_oper_accaunt.html", context)


# def oper_accaunt(request):
#     import locale
    
#     locale.setlocale(locale.LC_ALL, "")
    
#     title = "oper_accaunt"
#     type_url = "inside"
#     data = datetime.datetime.now()
#     year_now = datetime.datetime.now().year
#     month_now = datetime.datetime.now().month
    
    
#     category = CATEGORY_OPERACCOUNT
#     groupeis = GroupeOperaccount.objects.all()
    
#         # актуальные месяца нынешнего года
#     m = []
#     month_names = []
#     month_arr = []
#     for month in range(1, month_now+1):
#         month_name = MONTHS_RU[month - 1]

#         month_names.append({
#             "name_month": month_name,
#             "month": month,
#         })
#         month_arr.append([month_name])
#         m.append(month_name)

#     month_names.reverse()
#     month_arr.reverse()
#     m = str(m)

#     # Получаем операции
#     operations = (
#         Operation.objects.filter(operaccount__isnull=False, data__year__gte=year_now)
#         .select_related(
#             "operaccount",
#         )
#         .prefetch_related()
#         .order_by("-data")
#     )
#     # Создаем морфологический анализатор
#     morph = pymorphy3.MorphAnalyzer(lang="ru")
#     # Создаем словарь для группировки
#     operations_grouped = {}
    
#     # Группируем операции
#     for operation in operations:
#         # Получаем название месяца
#         month_name = morph.parse(operation.data.strftime("%B"))[0].normal_form.title()
#         account = operation.operaccount
#         category_id = account.category
        
#         # Создаем ключ для группировки
#         key = (month_name, account, category_id)
        
#         # Добавляем операцию в соответствующую группу
#         if key not in operations_grouped:
#             operations_grouped[key] = []
#         operations_grouped[key].append(operation)
    
#     # Преобразуем в список для удобства использования
#     operations_arr = []
#     for (month_name, account, category_id), operations_list in operations_grouped.items():
#         # Считаем общую сумму для группы
#         total = sum(op.amount for op in operations_list)
        
#         # Создаем запись для группы
#         group_data = {
#             'month': month_name,
#             'account': account,
#             'category': category_id,
#             'operations': operations_list,
#             'total': total
#         }
#         operations_arr.append(group_data)
#     # Сортируем по месяцу и категории
#     operations_arr.sort(key=lambda x: (x['month'], x['category']))

#     # Добавляем в контекст
#     context = {
#         "title": title,
#         "type_url": type_url,
#         "operations": operations_arr,
#         "groupeis": groupeis,
#         "category": category,
#         "month": m,
#     }
    
#     return render(request, "bank/inside/inside_one_oper_accaunt.html", context)

# def oper_accaunt(request):
#     title = "oper_accaunt"
#     type_url = "inside"
#     data = datetime.datetime.now()
#     year_now = datetime.datetime.now().year
#     month_now = datetime.datetime.now().month
    
#     # Получаем операции
#     operations = (
#         Operation.objects.filter(operaccount__isnull=False, data__year__gte=year_now)
#         .select_related("operaccount")
#         .prefetch_related()
#         .order_by("-data")
#     )
    
#     category = CATEGORY_OPERACCOUNT
#     groupeis = GroupeOperaccount.objects.all()
    
#     # Создаем морфологический анализатор
#     morph = pymorphy3.MorphAnalyzer(lang="ru")
    
#     # Создаем структуру для хранения данных по категориям
#     operations_by_category = {cat[0]: {} for cat in CATEGORY_OPERACCOUNT}
    
#     # Создаем список месяцев текущего года
#     months_current_year = []
#     for month in range(1, month_now + 1):
#         month_name = MONTHS_RU[month - 1]
#         months_current_year.append(month_name)
#     months_current_year.reverse()
    
#     # Инициализируем структуру данных для всех категорий и месяцев
#     for cat_id in operations_by_category:
#         for month in months_current_year:
#             operations_by_category[cat_id][month] = {
#                 'operations': [],
#                 'total': 0,
#                 'accounts': {}
#             }
    
#     # Группируем операции
#     for operation in operations:
#         month_name = morph.parse(operation.data.strftime("%B"))[0].normal_form.title()
#         account = operation.operaccount
#         category_id = account.category
        
#         if category_id in operations_by_category:
#             if month_name in operations_by_category[category_id]:
#                 # Добавляем операцию в соответствующий месяц и категорию
#                 operations_by_category[category_id][month_name]['operations'].append(operation)
#                 operations_by_category[category_id][month_name]['total'] += operation.amount
                
#                 # Группируем по счетам
#                 if account not in operations_by_category[category_id][month_name]['accounts']:
#                     operations_by_category[category_id][month_name]['accounts'][account] = {
#                         'operations': [],
#                         'total': 0
#                     }
#                 operations_by_category[category_id][month_name]['accounts'][account]['operations'].append(operation)
#                 operations_by_category[category_id][month_name]['accounts'][account]['total'] += operation.amount
    
#     # Преобразуем в список для шаблона
#     operations_arr = []
#     for cat_id, months_data in operations_by_category.items():
#         category_data = {
#             'category_id': cat_id,
#             'months': []
#         }
        
#         for month_name in months_current_year:
#             month_data = months_data[month_name]
#             month_info = {
#                 'month': month_name,
#                 'total': month_data['total'],
#                 'accounts': []
#             }
            
#             # Добавляем данные по счетам
#             for account, account_data in month_data['accounts'].items():
#                 account_info = {
#                     'account': account,
#                     'operations': account_data['operations'],
#                     'total': account_data['total']
#                 }
#                 month_info['accounts'].append(account_info)
            
#             category_data['months'].append(month_info)
        
#         operations_arr.append(category_data)
    
#     context = {
#         "title": title,
#         "type_url": type_url,
#         "operations": operations_arr,
#         "groupeis": groupeis,
#         "category": category,
#         "months": months_current_year,
#     }
    
#     return render(request, "bank/inside/inside_one_oper_accaunt.html", context)

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
    
    # Создаем список месяцев текущего года
    months_current_year = []
    for month in range(1, month_now + 1):
        month_name = MONTHS_RU[month - 1]
        months_current_year.append(month_name)
    months_current_year.reverse()
    print(months_current_year)
    
    # Инициализируем структуру данных для всех категорий, счетов и месяцев
    for cat_id, cat_data in operations_by_category.items():
        # Получаем все счета для данной категории
        accounts = groupeis.filter(category=cat_id)
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
            for month_name in months_current_year:
                month_data = account_data['months'][month_name]
                month_info = {
                    'month': month_name,
                    'operations': month_data['operations'],
                    'total': month_data['total']
                }
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
