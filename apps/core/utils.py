import datetime
from django.db.models.functions import ExtractMonth
from apps.bank.models import CATEGORY_OPERACCOUNT
from apps.core.models import LogsError, Logsinfo
import pymorphy3
import locale
import copy
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
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.db.models.functions import TruncMonth
from django.db.models import Prefetch, OuterRef
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q, F, OrderBy, Case, When, Value


def error_alert(error, location, info):
    error_alert = LogsError.objects.create(location=location, info=info)


def log_alert(location, info):
    error_alert = Logsinfo.objects.create(location=location, info=info)


def create_month_categ_persent():
    pass


def get_id_categ_oper(id_nalog):
    for categ_oper_for in CATEGORY_OPERACCOUNT:
        name = categ_oper_for[1]
        id = categ_oper_for[0]

        if id_nalog == id:
            return name


def fill_operations_arrays_ooo(
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
    is_old_oper,
    old_oper_arr,
):
    between_id_for_arr_in_out_all = cate_oper_beetwen_by_name.get("ПРЕМИИ")
    between_id_for_remainder_ip = cate_oper_beetwen_by_name.get(
        "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП"
    )
    between_id_for_out_ip_suborder = cate_oper_beetwen_by_name.get(
        "перевод на ИП для оплаты субподряда"
    )
    categ_percent_crp = categ_percent_by_name.get("ПРИБЫЛЬ 1% ЦРП 5%")

    categ_percent_crp_kv = categ_percent_by_name.get("КВ 20% ЦРП 50%")

    categ_percent_ycn = categ_percent_by_name.get(
        "НАЛОГ УСН ООО доход-расходы*15% ЦРП 2- ТРП 1,5% (отложенные на выплату)"
    )
    categ_percent_ycn_2 = categ_percent_by_name.get(
        "Реальный налог УСН с ООО доход - 1%"
    )

    categoru_nalog_ysn = categoru_nalog.get(name="ФАКТИЧЕСКАЯ ОПЛАТА УСН")

    if is_old_oper:

        def reverse_months_in_dict(d):
            if isinstance(d, dict):
                months = [m for m in MONTHS_RU if m in d]
                if len(months) == 12 and set(months) == set(MONTHS_RU):
                    # Это словарь месяцев, разворачиваем в прямой порядок (январь → декабрь)
                    items = [(m, d[m]) for m in MONTHS_RU if m in d]
                    return {k: reverse_months_in_dict(v) for k, v in items}
                else:
                    return {k: reverse_months_in_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [reverse_months_in_dict(x) for x in d]
            else:
                return d

        # Группировка операций по годам
        operations_by_year = {}
        # Получаем уникальные года из операций
        years = set()
        for operation in operations:
            years.add(operation.data.year)
        for year in sorted(years):
            # Фильтруем операции за этот год
            operations_year = [op for op in operations if op.data.year == year]
            # Копируем структуры для этого года
            arr_in_y = copy.deepcopy(arr_in)
            arr_out_y = copy.deepcopy(arr_out)
            arr_in_out_all_y = copy.deepcopy(arr_in_out_all)
            arr_inside_all_y = copy.deepcopy(arr_inside_all)
            arr_in_out_after_all_y = copy.deepcopy(arr_in_out_after_all)
            arr_in_out_after_all_total_y = copy.deepcopy(arr_in_out_after_all_total)
            arr_start_month_y = copy.deepcopy(arr_start_month)
            # months_current_year для этого года
            months_year = [MONTHS_RU[month - 1] for month in range(1, 13)]
            months_year.reverse()
            month_numbers_year = {month: i + 1 for i, month in enumerate(months_year)}

            # --- ОСНОВНОЙ КОД ОБРАБОТКИ ДЛЯ КАЖДОГО ГОДА ---
            # Добавляем категории из CATEGORY_OPERACCOUNT
            for categ_oper in CATEGORY_OPERACCOUNT:
                arr_inside_all_y["category"][2]["group"][categ_oper[1]] = {}
                for i, month in enumerate(months_year):
                    arr_inside_all_y["category"][2]["group"][categ_oper[1]][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

            # Добавляем месяцы
            for i, month in enumerate(months_year):
                month_number = month_numbers_year[month]
                arr_out_y["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": f"{month_number:02d}",
                    "is_make_operations": False,
                }
                # рс на анчало меясца
                arr_start_month_y["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                # первый блок доход расход
                for in_out in arr_in_out_all_y["category"]:

                    in_out["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    if in_out["name"] == "ПРИБЫЛЬ 1% ЦРП 5%":
                        in_out["total"][month]["is_make_operations"] = True
                        in_out["total"][month]["type_operations"] = "percent"

                        in_out["total"][month]["date_start"] = datetime.datetime(
                            year_now, MONTHS_RU.index(month) + 1, 1
                        )
                        in_out["total"][month]["id_groupe"] = categ_percent_crp["id"]
                        in_out["total"][month]["between_id"] = categ_percent_crp[
                            "category_between"
                        ]
                        in_out["total"][month]["bank_out"] = categ_percent_crp[
                            "category_between__bank_to"
                        ]
                        in_out["total"][month]["amount_month_chek"] = 0
                        in_out["total"][month]["chek"] = False

                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_crp["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        in_out["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        in_out["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )

                    elif in_out["name"] == "КВ 20% ЦРП 50%":
                        in_out["total"][month]["is_make_operations"] = True
                        in_out["total"][month]["type_operations"] = "percent"

                        in_out["total"][month]["date_start"] = datetime.datetime(
                            year_now, MONTHS_RU.index(month) + 1, 1
                        )
                        in_out["total"][month]["id_groupe"] = categ_percent_crp_kv["id"]
                        in_out["total"][month]["between_id"] = categ_percent_crp_kv[
                            "category_between"
                        ]
                        in_out["total"][month]["bank_out"] = categ_percent_crp_kv[
                            "category_between__bank_to"
                        ]
                        in_out["total"][month]["amount_month_chek"] = 0
                        in_out["total"][month]["chek"] = False

                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_crp_kv["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        in_out["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        in_out["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )

                    elif in_out["name"] == "ПРЕМИИ":
                        in_out["total"][month]["is_make_operations"] = True
                        in_out["total"][month]["bank_out"] = (
                            between_id_for_arr_in_out_all["bank_to"]
                        )
                        in_out["total"][month]["date_start"] = datetime.datetime(
                            year_now, MONTHS_RU.index(month) + 1, 1
                        )
                        in_out["total"][month]["operation_id"] = 0
                        in_out["total"][month]["type_operations"] = "between"
                        in_out["total"][month]["between_id"] = (
                            between_id_for_arr_in_out_all["id"]
                        )

                # второй блок доход расход
                for after_all in arr_in_out_after_all_y["category"]:
                    after_all["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    if (
                        after_all["name"]
                        == "НАЛОГ УСН ООО доход-расходы*15% ЦРП 2- ТРП 1,5% (отложенные на выплату)"
                    ):
                        after_all["total"][month]["is_make_operations"] = True
                        after_all["total"][month]["type_operations"] = "percent"

                        after_all["total"][month]["date_start"] = datetime.datetime(
                            year_now, MONTHS_RU.index(month) + 1, 1
                        )
                        after_all["total"][month]["id_groupe"] = categ_percent_ycn["id"]
                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_ycn["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        after_all["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        after_all["total"][month]["operation_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )

                    elif after_all["name"] == "Реальный налог УСН с ООО доход - 1%":
                        after_all["total"][month]["is_make_operations"] = True
                        after_all["total"][month]["type_operations"] = "percent"

                        after_all["total"][month]["date_start"] = datetime.datetime(
                            year_now, MONTHS_RU.index(month) + 1, 1
                        )
                        after_all["total"][month]["id_groupe"] = categ_percent_ycn_2[
                            "id"
                        ]
                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_ycn_2["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        after_all["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        after_all["total"][month]["operation_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )

                # третий блок доход расход  arr_in_out_after_all_total
                for after_all_total in arr_in_out_after_all_total_y["category"]:
                    after_all_total["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    if after_all_total["name"] == "ФАКТИЧЕСКАЯ ОПЛАТА УСН":

                        after_all_total["total"][month]["is_make_operations"] = True
                        after_all_total["total"][month]["bank_out"] = 5
                        after_all_total["total"][month]["date_start"] = (
                            datetime.datetime(year_now, MONTHS_RU.index(month) + 1, 1)
                        )
                        after_all_total["total"][month]["operation_id"] = 0
                        after_all_total["total"][month]["type_operations"] = "nalog"
                        after_all_total["total"][month]["id_groupe"] = (
                            categoru_nalog_ysn["id"]
                        )

                    elif after_all_total["name"] == "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП":
                        after_all_total["total"][month]["is_make_operations"] = True
                        after_all_total["total"][month]["bank_out"] = (
                            between_id_for_remainder_ip["bank_to"]
                        )
                        after_all_total["total"][month]["date_start"] = (
                            datetime.datetime(year_now, MONTHS_RU.index(month) + 1, 1)
                        )
                        after_all_total["total"][month]["operation_id"] = 0
                        after_all_total["total"][month]["type_operations"] = "between"
                        after_all_total["total"][month]["between_id"] = (
                            between_id_for_remainder_ip["id"]
                        )

                # внутренние счета расходы все
                arr_inside_all_y["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }

                for inside_all in arr_inside_all_y["category"]:
                    inside_all["total"]["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    if inside_all["name"] == "НАЛОГИ (без УСН):":
                        inside_all["group"]["ИТОГО налоги с ЗП:"][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                        }

            # months_year
            for service in services:
                name = f"{service.name}({service.name_long_ru})"
                arr_in_y["category"][0]["group"][name] = {}

                for i, month in enumerate(months_year):
                    month_number = month_numbers_year[month]

                    # Для услуг
                    arr_in_y["category"][0]["group"][name][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

                    # # Для переводов с ИП
                    # arr_in_y["category"][1]["group"][
                    #     "перевод с ИП для оплаты субподряда"
                    # ][month] = {
                    #     "amount_month": 0,
                    #     "month_number": MONTHS_RU.index(month) + 1,
                    #     "is_make_operations": False,
                    # }

                    # # Для переводов с $
                    # arr_in_y["category"][1]["group"][
                    #     "перевод с $ для оплаты субподряда"
                    # ][month] = {
                    #     "amount_month": 0,
                    #     "month_number": MONTHS_RU.index(month) + 1,
                    #     "is_make_operations": False,
                    # }
                    # Для переводов с хранилища
                    arr_in_y["category"][1]["group"]["зачисление из хранилища"][
                        month
                    ] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

                    # Для итогов
                    arr_in_y["total_category"]["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

                    # Для arr_out
                    # Добавляем месяцы для SEO
                    arr_out_y["category"][0]["group"]["SEO"]["Topvisor"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": True,
                        "bank_out": 5,
                        "date_start": datetime.datetime(
                            year_now, MONTHS_RU.index(month) + 1, 1
                        ),
                        "operation_id": 0,
                        "id_groupe": 2,
                        "type_operations": "SubcontractOtherCategory",
                        "expected": 0,
                    }
                    arr_out_y["category"][0]["group"]["SEO"]["ИП Галаев"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }
                    arr_out_y["category"][0]["group"]["SEO"]["Другое"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                        "expected": 0,
                    }

                    # Добавляем месяцы для переводов

                    arr_out_y["category"][1]["group"][
                        "перевод на ИП для оплаты субподряда"
                    ][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": True,
                        "bank_out": between_id_for_out_ip_suborder["bank_to"],
                        "date_start": datetime.datetime(
                            year_now, MONTHS_RU.index(month) + 1, 1
                        ),
                        "operation_id": 0,
                        "type_operations": "between",
                        "between_id": between_id_for_out_ip_suborder["id"],
                        "expected": 0,
                    }

                    # Добавляем месяцы для других субподрядов
                    for category in other_categ_subkontract:

                        if category.name not in arr_out_y["category"][2]["group"]:
                            arr_out_y["category"][2]["group"][category.name] = {}
                            # Инициализируем месяцы для каждой категории
                            for i, month in enumerate(months_year):
                                month_number = month_numbers_year[month]
                                arr_out_y["category"][2]["group"][category.name][
                                    month
                                ] = {
                                    "amount_month": 0,
                                    "month_number": MONTHS_RU.index(month) + 1,
                                    "is_make_operations": True,
                                    "bank_out": 5,
                                    "date_start": datetime.datetime(
                                        year_now, MONTHS_RU.index(month) + 1, 1
                                    ),
                                    "operation_id": 0,
                                    "type_operations": "SubcontractOtherCategory",
                                    "id_groupe": category.id,
                                    "expected": 0,
                                }

                    # Добавляем месяцы для итогов arr_out
                    arr_out_y["total_category"]["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

            # Добавляем сервисы в "другое" для arr_out, исключая SEO

            for service in services:
                if service.name != "SEO":  # Пропускаем SEO
                    name = f"{service.name}({service.name_long_ru})"
                    arr_out_y["category"][0]["group"]["остальное"][name] = {}
                    for i, month in enumerate(months_year):
                        arr_out_y["category"][0]["group"]["остальное"][name][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                            "is_make_operations": False,
                        }

            # распределение операций
            for operation in operations_year:
                month_name = MONTHS_RU[operation.data.month - 1]
                prev_month = (
                    MONTHS_RU[operation.data.month]
                    if operation.data.month < 12
                    else None
                )
                is_prev_month = prev_month in months_year if prev_month else False
                # операции ВНУТРЕННИЕ СЧЕТА
                if operation.operaccount:
                    id_operacc_categ = get_id_categ_oper(operation.operaccount.category)
                    arr_inside_all_y["category"][2]["group"][id_operacc_categ][
                        month_name
                    ]["amount_month"] += operation.amount
                    arr_inside_all_y["category"][2]["total"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                    arr_inside_all_y["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                elif operation.salary and operation.employee:
                    pass
                    # 10 число в след месяц
                    if operation.salary.id == 1:
                        month_name = MONTHS_RU[operation.data.month - 2]
                        if (
                            month_name
                            in arr_inside_all_y["category"][1]["total"]["total"]
                        ):
                            arr_inside_all_y["category"][1]["total"]["total"][
                                month_name
                            ]["amount_month"] += operation.amount
                            arr_inside_all_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount

                    # не 10 число обычно
                    else:
                        arr_inside_all_y["category"][1]["total"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_inside_all_y["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                elif operation.nalog:

                    if operation.nalog.id != 4 and operation.nalog.id != 9:

                        arr_inside_all_y["category"][0]["group"]["ИТОГО налоги с ЗП:"][
                            month_name
                        ]["amount_month"] += operation.amount
                        arr_inside_all_y["category"][0]["total"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_inside_all_y["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

                    elif operation.nalog.id == 4:

                        arr_inside_all_y["category"][0]["total"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_inside_all_y["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                    elif operation.nalog.id == 9:

                        arr_in_out_after_all_total_y["category"][1]["total"][
                            month_name
                        ]["amount_month"] += operation.amount
                        arr_in_out_after_all_total_y["category"][1]["total"][
                            month_name
                        ]["operation_id"] = operation.id

                # операции прихода по договорам услуг
                elif operation.monthly_bill and operation.suborder is None:
                    # поступления по договорам услуг

                    service_name = f"{operation.monthly_bill.service.name}({operation.monthly_bill.service.name_long_ru})"

                    if service_name in arr_in_y["category"][0]["group"]:
                        arr_in_y["category"][0]["group"][service_name][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_in_y["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

                # операции расхода по договорам услуг
                elif operation.suborder:
                    print("operation.suborder",operation)
                    # расходы по договорам услуг
                    # Для SEO
                    if operation.suborder.month_bill.service.name == "SEO":

                        if (
                            operation.suborder.category_employee
                            and operation.suborder.category_employee.name == "ИП Галаев"
                        ):
                            arr_out_y["category"][0]["group"]["SEO"]["ИП Галаев"][
                                month_name
                            ]["amount_month"] += operation.amount
                        else:
                            arr_out_y["category"][0]["group"]["SEO"]["Другое"][
                                month_name
                            ]["amount_month"] += operation.amount

                    # Для других субподрядов
                    else:

                        service_name = f"{operation.suborder.month_bill.service.name}({operation.suborder.month_bill.service.name_long_ru})"
                        if (
                            service_name
                            in arr_out_y["category"][0]["group"]["остальное"]
                        ):
                            arr_out_y["category"][0]["group"]["остальное"][
                                service_name
                            ][month_name]["amount_month"] += operation.amount
                            arr_out_y["category"][0]["group"]["остальное"][
                                service_name
                            ][month_name]["operation_id"] = operation.id
                    # Добавляем в общий итог по месяцу операции
                    arr_out_y["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                elif operation.suborder_other:
                    print("operation.suborder_other",operation)
                    # # Добавляем в общий итог по месяцу операции
                    arr_out_y["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                    if operation.suborder_other.name == "Topvisor":
                        arr_out_y["category"][0]["group"]["SEO"]["Topvisor"][
                            month_name
                        ]["amount_month"] += operation.amount
                        arr_out_y["category"][0]["group"]["SEO"]["Topvisor"][
                            month_name
                        ]["operation_id"] = operation.id
                        if is_prev_month:
                            arr_out_y["category"][0]["group"]["SEO"]["Topvisor"][
                                prev_month
                            ]["expected"] += operation.amount

                    else:
                        service_name = operation.suborder_other.name
                        arr_out_y["category"][2]["group"][service_name][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_out_y["category"][2]["group"][service_name][month_name][
                            "operation_id"
                        ] = operation.id
                        if is_prev_month:
                            arr_out_y["category"][2]["group"][service_name][prev_month][
                                "expected"
                            ] += operation.amount
                # операции между счетами
                elif operation.between_bank:
                    if operation.bank_in == bank:
                        if (
                            operation.between_bank.name
                            == "перевод на ИП для оплаты субподряда"
                        ):
                            arr_out_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "перевод на ИП для оплаты субподряда"
                            ][month_name]["amount_month"] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "перевод на ИП для оплаты субподряда"
                            ][month_name]["operation_id"] = operation.id

                            if is_prev_month:
                                arr_out_y["category"][1]["group"][
                                    "перевод на ИП для оплаты субподряда"
                                ][prev_month]["expected"] += operation.amount
                        elif operation.between_bank.name == "ПРЕМИИ":

                            name_to_find = "ПРЕМИИ"
                            item = next(
                                (
                                    x
                                    for x in arr_in_out_all_y["category"]
                                    if x["name"] == name_to_find
                                ),
                                None,
                            )
                            if item:
                                item["total"][month_name][
                                    "amount_month"
                                ] += operation.amount
                                item["total"][month_name]["operation_id"] = operation.id
                        elif (
                            operation.between_bank.name
                            == "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП"
                        ):
                            name_to_find = "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП"
                            item = next(
                                (
                                    x
                                    for x in arr_in_out_after_all_total_y["category"]
                                    if x["name"] == name_to_find
                                ),
                                None,
                            )
                            if item:
                                item["total"][month_name][
                                    "amount_month"
                                ] += operation.amount
                                item["total"][month_name]["operation_id"] = operation.id
                        elif operation.between_bank.name == "ПРИБЫЛЬ 1% ЦРП 5%":
                            name_to_find = "ПРИБЫЛЬ 1% ЦРП 5%"

                            item = next(
                                (
                                    x
                                    for x in arr_in_out_all_y["category"]
                                    if x["name"] == name_to_find
                                ),
                                None,
                            )
                            if item:
                                item["total"][month_name][
                                    "amount_month_chek"
                                ] += operation.amount
                                item["total"][month_name]["operation_id"] = operation.id
                                item["total"][month_name]["chek"] = True
                        elif operation.between_bank.name == "КВ 20% ЦРП 50%":
                            name_to_find = "КВ 20% ЦРП 50%"

                            item = next(
                                (
                                    x
                                    for x in arr_in_out_all_y["category"]
                                    if x["name"] == name_to_find
                                ),
                                None,
                            )
                            if item:
                                item["total"][month_name][
                                    "amount_month_chek"
                                ] += operation.amount
                                item["total"][month_name]["operation_id"] = operation.id
                                item["total"][month_name]["chek"] = True
                    elif operation.bank_to == bank:
                        arr_in_y["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        if operation.between_bank.name == "зачисление на ООО":
                            arr_in_y["category"][1]["group"]["зачисление из хранилища"][
                                month_name
                            ]["operation_id"] = operation.id
                            arr_in_y["category"][1]["group"]["зачисление из хранилища"][
                                month_name
                            ]["amount_month"] += operation.amount
                else:
                    # операции между счетами
                    # операции расход
                    if operation.bank_in == bank:
                        arr_out_y["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        if operation.bank_to.id == 2:
                            arr_out_y["category"][1]["group"][
                                "перевод на ИП для оплаты субподряда"
                            ][month_name]["amount_month"] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "перевод на ИП для оплаты субподряда"
                            ][month_name]["operation_id"] = operation.id

                            if is_prev_month:
                                arr_out_y["category"][1]["group"][
                                    "перевод на ИП для оплаты субподряда"
                                ][prev_month]["expected"] += operation.amount
                    # операции доход:
                    else:
                        pass

            # разные общие суммы
            for i, month in enumerate(months_year):
                # === Расчет "РЕАЛЬНЫЕ ПОСТУПЛЕНИЯ ООО (ВЫРУЧКА-СУБПОДРЯД И БУХ)" ===
                in_sum = (
                    arr_in_y["total_category"]["total"]
                    .get(month, {})
                    .get("amount_month", 0)
                )
                out_sum = (
                    arr_out_y["total_category"]["total"]
                    .get(month, {})
                    .get("amount_month", 0)
                )

                if month not in arr_in_out_all_y["category"][0]["total"]:
                    arr_in_out_all_y["category"][0]["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                diff_in_out = in_sum - out_sum
                arr_in_out_all_y["category"][0]["total"][month][
                    "amount_month"
                ] = diff_in_out

                # ПРИБЫЛЬ 1% ЦРП 5%
                if arr_in_out_all_y["category"][1]["total"][month]["chek"] == True:

                    in_out_all_crp = arr_in_out_all_y["category"][1]["total"][month][
                        "amount_month_chek"
                    ]
                else:
                    in_out_all_crp = (
                        diff_in_out
                        * arr_in_out_all_y["category"][1]["total"][month]["percent"]
                        / 100
                    )
                arr_in_out_all_y["category"][1]["total"][month][
                    "amount_month"
                ] = in_out_all_crp

                # КВ 20% ЦРП 50%
                if arr_in_out_all_y["category"][2]["total"][month]["chek"] == True:

                    in_out_all_crp_kv = arr_in_out_all_y["category"][2]["total"][month][
                        "amount_month_chek"
                    ]

                else:
                    in_out_all_crp_kv = (
                        diff_in_out
                        * arr_in_out_all_y["category"][2]["total"][month]["percent"]
                        / 100
                    )
                arr_in_out_all_y["category"][2]["total"][month][
                    "amount_month"
                ] = in_out_all_crp_kv

                # ИТОГО  РЕАЛЬНЫЕ ПОСТУПЛЕНИЯ ООО (ВЫРУЧКА-СУБПОДРЯД И БУХ)
                in_out_all_total = (
                    in_out_all_crp
                    + in_out_all_crp_kv
                    + arr_in_out_all_y["category"][3]["total"][month]["amount_month"]
                )
                arr_in_out_all_y["category"][4]["total"][month][
                    "amount_month"
                ] = in_out_all_total

                # ДОХОД - РЕАЛЬНЫЙ РАСХОД в текущем месяце
                all_out_dop = arr_inside_all_y["total_category"]["total"][month][
                    "amount_month"
                ]

                diff_in_out_real = in_sum - out_sum - all_out_dop - in_out_all_total
                arr_in_out_after_all_y["category"][0]["total"][month][
                    "amount_month"
                ] = diff_in_out_real

                # НАЛОГ УСН ООО доход-расходы*15% ЦРП 2- ТРП 1,5% (отложенные на выплату)
                ycno = (
                    in_sum
                    * arr_in_out_after_all_y["category"][1]["total"][month]["percent"]
                    / 100
                )
                arr_in_out_after_all_y["category"][1]["total"][month][
                    "amount_month"
                ] = ycno

                # Реальный налог УСН с ООО доход - 1%
                arr_in_out_after_all_y["category"][2]["total"][month][
                    "amount_month"
                ] = (
                    in_sum
                    * arr_in_out_after_all_y["category"][2]["total"][month]["percent"]
                    / 100
                )

                # ПРОВЕРКА ДОХОД - РАСХОД
                arr_in_out_after_all_y["category"][3]["total"][month][
                    "amount_month"
                ] = (diff_in_out_real - ycno)

                # ПРОВЕРКА ООО ДОХОД-РАСХОД = ОСТАТОК из первого общего блока
                arr_in_out_all_y["category"][5]["total"][month]["amount_month"] = (
                    diff_in_out_real - ycno
                )

                # ДОХОД-РАСХОД (в текущем месяце без УСН и вывода остатков)
                arr_in_out_after_all_total_y["category"][0]["total"][month][
                    "amount_month"
                ] = diff_in_out_real

                # ОСТАТОК на Р/С на конец месяца (после уплаты УСН и вывода остатков)
                nalog_ycn = arr_in_out_after_all_total_y["category"][1]["total"][month][
                    "amount_month"
                ]
                to_ip = arr_in_out_after_all_total_y["category"][2]["total"][month][
                    "amount_month"
                ]

                for i, month in enumerate(months_year):

                    if i + 1 < len(months_year):
                        month_prev = months_year[i + 1]
                        prev_all_sum_month = arr_in_out_after_all_total_y["category"][
                            3
                        ]["total"][month_prev]["amount_month"]
                    else:
                        prev_year = year - 1
                        last_month = "Декабрь"
                        prev_all_sum_month = 0
                        prev_year_data = operations_by_year.get(prev_year)
                        if prev_year_data:
                            try:
                                category_list = prev_year_data[
                                    "arr_in_out_after_all_total"
                                ]["category"]
                                prev_all_sum_month = category_list[3]["total"][
                                    last_month
                                ]["amount_month"]
                            except Exception as e:

                                prev_all_sum_month = 0

                    all_sum_month = (
                        diff_in_out_real - nalog_ycn - to_ip + prev_all_sum_month
                    )
                    arr_in_out_after_all_total_y["category"][3]["total"][month][
                        "amount_month"
                    ] = all_sum_month

                # Р/С на начало месяца
                # получить следующий месяц

                for i, month in enumerate(months_year):
                    if i == len(months_year) - 1:
                        # Для самого последнего месяца (например, "Январь") — остаток на конец декабря прошлого года
                        prev_year = year - 1
                        last_month = "Декабрь"
                        last_balance = 0
                        prev_year_data = operations_by_year.get(prev_year)
                        if prev_year_data:

                            try:
                                category_list = prev_year_data[
                                    "arr_in_out_after_all_total"
                                ]["category"]

                                last_balance = category_list[3]["total"][last_month][
                                    "amount_month"
                                ]
                            except Exception as e:
                                print("Ошибка при доступе к остатку прошлого года:", e)
                                last_balance = 0
                        arr_start_month_y["total"][month]["amount_month"] = last_balance
                    else:
                        next_month = months_year[i + 1]
                        arr_start_month_y["total"][month]["amount_month"] = (
                            arr_in_out_after_all_total_y["category"][3]["total"][
                                next_month
                            ]["amount_month"]
                        )

            arr_in_y = reverse_months_in_dict(arr_in_y)
            arr_out_y = reverse_months_in_dict(arr_out_y)
            arr_in_out_all_y = reverse_months_in_dict(arr_in_out_all_y)
            arr_inside_all_y = reverse_months_in_dict(arr_inside_all_y)
            arr_in_out_after_all_y = reverse_months_in_dict(arr_in_out_after_all_y)
            arr_in_out_after_all_total_y = reverse_months_in_dict(
                arr_in_out_after_all_total_y
            )
            arr_start_month_y = reverse_months_in_dict(arr_start_month_y)

            months_year = list(reversed(months_year))

            operations_actual = {
                "arr_in": arr_in_y,
                "arr_out": arr_out_y,
                "arr_in_out_all": arr_in_out_all_y,
                "arr_inside_all": arr_inside_all_y,
                "arr_in_out_after_all": arr_in_out_after_all_y,
                "arr_in_out_after_all_total": arr_in_out_after_all_total_y,
                "arr_start_month": arr_start_month_y,
                "months_current_year": months_year,
                "year": year,
            }
            operations_by_year[year] = operations_actual

        operations_by_year = dict(sorted(operations_by_year.items(), reverse=True))
        return operations_by_year
    else:
        between_id_for_arr_in_out_all = cate_oper_beetwen_by_name.get("ПРЕМИИ")
        between_id_for_remainder_ip = cate_oper_beetwen_by_name.get(
            "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП"
        )
        between_id_for_out_ip_suborder = cate_oper_beetwen_by_name.get(
            "перевод на ИП для оплаты субподряда"
        )
        categ_percent_crp = categ_percent_by_name.get("ПРИБЫЛЬ 1% ЦРП 5%")
        categ_percent_crp_kv = categ_percent_by_name.get("КВ 20% ЦРП 50%")
        categ_percent_ycn = categ_percent_by_name.get(
            "НАЛОГ УСН ООО доход-расходы*15% ЦРП 2- ТРП 1,5% (отложенные на выплату)"
        )
        categ_percent_ycn_2 = categ_percent_by_name.get(
            "Реальный налог УСН с ООО доход - 1%"
        )

        categoru_nalog_ysn = categoru_nalog.get(name="ФАКТИЧЕСКАЯ ОПЛАТА УСН")

        for categ_oper in CATEGORY_OPERACCOUNT:

            arr_inside_all["category"][2]["group"][categ_oper[1]] = {}
            # Добавляем месяцы для каждой категории
            for i, month in enumerate(months_current_year):
                month_number = month_numbers[month]
                arr_inside_all["category"][2]["group"][categ_oper[1]][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

        # Добавляем месяцы
        for i, month in enumerate(months_current_year):
            # month_name = MONTHS_RU[operation.data.month - 1]
            

            month_number = month_numbers[month]
            prev_month = (
                MONTHS_RU[month_number] if month_number < 12 else None
            )
            is_prev_month = prev_month in months_current_year if prev_month else False
           
            arr_out["total_category"]["total"][month] = {
                "amount_month": 0,
                "month_number": f"{month_number:02d}",
                "is_make_operations": False,
            }
            # рс на анчало меясца
            arr_start_month["total"][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
            }
            # первый блок доход расход
            for in_out in arr_in_out_all["category"]:

                in_out["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                if in_out["name"] == "ПРИБЫЛЬ 1% ЦРП 5%":
                    in_out["total"][month]["is_make_operations"] = True
                    in_out["total"][month]["type_operations"] = "percent"

                    in_out["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    in_out["total"][month]["id_groupe"] = categ_percent_crp["id"]
                    in_out["total"][month]["between_id"] = categ_percent_crp[
                        "category_between"
                    ]
                    in_out["total"][month]["bank_out"] = categ_percent_crp[
                        "category_between__bank_to"
                    ]
                    in_out["total"][month]["amount_month_chek"] = 0
                    in_out["total"][month]["chek"] = False

                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_crp["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    in_out["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    in_out["total"][month]["operation_percent_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )
                    

                elif in_out["name"] == "КВ 20% ЦРП 50%":
                    in_out["total"][month]["is_make_operations"] = True
                    in_out["total"][month]["type_operations"] = "percent"

                    in_out["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    in_out["total"][month]["id_groupe"] = categ_percent_crp_kv["id"]
                    in_out["total"][month]["between_id"] = categ_percent_crp_kv[
                        "category_between"
                    ]
                    in_out["total"][month]["bank_out"] = categ_percent_crp_kv[
                        "category_between__bank_to"
                    ]
                    in_out["total"][month]["amount_month_chek"] = 0
                    in_out["total"][month]["chek"] = False

                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_crp_kv["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    in_out["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    in_out["total"][month]["operation_percent_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )

                elif in_out["name"] == "ПРЕМИИ":
                    in_out["total"][month]["is_make_operations"] = True
                    in_out["total"][month]["bank_out"] = between_id_for_arr_in_out_all[
                        "bank_to"
                    ]
                    in_out["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    in_out["total"][month]["operation_id"] = 0
                    in_out["total"][month]["type_operations"] = "between"
                    in_out["total"][month]["between_id"] = (
                        between_id_for_arr_in_out_all["id"]
                    )
                    in_out["total"][month]["expected"] = 0

            # второй блок доход расход
            for after_all in arr_in_out_after_all["category"]:
                after_all["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                if (
                    after_all["name"]
                    == "НАЛОГ УСН ООО доход-расходы*15% ЦРП 2- ТРП 1,5% (отложенные на выплату)"
                ):
                    after_all["total"][month]["is_make_operations"] = True
                    after_all["total"][month]["type_operations"] = "percent"

                    after_all["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    after_all["total"][month]["id_groupe"] = categ_percent_ycn["id"]
                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_ycn["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    after_all["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    after_all["total"][month]["operation_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )
                         

                elif after_all["name"] == "Реальный налог УСН с ООО доход - 1%":
                    after_all["total"][month]["is_make_operations"] = True
                    after_all["total"][month]["type_operations"] = "percent"

                    after_all["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    after_all["total"][month]["id_groupe"] = categ_percent_ycn_2["id"]
                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_ycn_2["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    after_all["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    after_all["total"][month]["operation_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )

            # третий блок доход расход  arr_in_out_after_all_total
            for after_all_total in arr_in_out_after_all_total["category"]:
                after_all_total["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                if after_all_total["name"] == "ФАКТИЧЕСКАЯ ОПЛАТА УСН":

                    after_all_total["total"][month]["is_make_operations"] = True
                    after_all_total["total"][month]["bank_out"] = 5
                    after_all_total["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    after_all_total["total"][month]["operation_id"] = 0
                    after_all_total["total"][month]["type_operations"] = "nalog"
                    after_all_total["total"][month]["id_groupe"] = categoru_nalog_ysn[
                        "id"
                    ]

                elif after_all_total["name"] == "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП":
                    after_all_total["total"][month]["is_make_operations"] = True
                    after_all_total["total"][month]["bank_out"] = (
                        between_id_for_remainder_ip["bank_to"]
                    )
                    after_all_total["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    after_all_total["total"][month]["operation_id"] = 0
                    after_all_total["total"][month]["type_operations"] = "between"
                    after_all_total["total"][month]["between_id"] = (
                        between_id_for_remainder_ip["id"]
                    )

            # внутренние счета расходы все
            arr_inside_all["total_category"]["total"][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
            }

            for inside_all in arr_inside_all["category"]:
                inside_all["total"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                if inside_all["name"] == "НАЛОГИ (без УСН):":
                    inside_all["group"]["ИТОГО налоги с ЗП:"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }

        for service in services:
            name = f"{service.name}({service.name_long_ru})"
            arr_in["category"][0]["group"][name] = {}

            for i, month in enumerate(months_current_year):
                month_number = month_numbers[month]

                # Для услуг
                arr_in["category"][0]["group"][name][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

                # # Для переводов с ИП
                # arr_in["category"][1]["group"]["перевод с ИП для оплаты субподряда"][
                #     month
                # ] = {
                #     "amount_month": 0,
                #     "month_number": MONTHS_RU.index(month) + 1,
                #     "is_make_operations": False,
                # }

                # # Для переводов с $
                # arr_in["category"][1]["group"]["перевод с $ для оплаты субподряда"][
                #     month
                # ] = {
                #     "amount_month": 0,
                #     "month_number": MONTHS_RU.index(month) + 1,
                #     "is_make_operations": False,
                # }
                # Для переводов с хранилища
                arr_in["category"][1]["group"]["зачисление из хранилища"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

                # Для итогов
                arr_in["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

                # Для arr_out
                # Добавляем месяцы для SEO
                arr_out["category"][0]["group"]["SEO"]["Topvisor"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": True,
                    "bank_out": 5,
                    "date_start": datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "id_groupe": 2,
                    "type_operations": "SubcontractOtherCategory",
                    "expected": 0,
                }
                arr_out["category"][0]["group"]["SEO"]["ИП Галаев"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }
                arr_out["category"][0]["group"]["SEO"]["Другое"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                    "expected": 0,
                }

                # Добавляем месяцы для переводов

                arr_out["category"][1]["group"]["перевод на ИП для оплаты субподряда"][
                    month
                ] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": True,
                    "bank_out": between_id_for_out_ip_suborder["bank_to"],
                    "date_start": datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "type_operations": "between",
                    "between_id": between_id_for_out_ip_suborder["id"],
                    "expected": 0,
                }

                # Добавляем месяцы для других субподрядов
                for category in other_categ_subkontract:

                    if category.name not in arr_out["category"][2]["group"]:
                        arr_out["category"][2]["group"][category.name] = {}
                        # Инициализируем месяцы для каждой категории
                        for i, month in enumerate(months_current_year):
                            month_number = month_numbers[month]
                            arr_out["category"][2]["group"][category.name][month] = {
                                "amount_month": 0,
                                "month_number": MONTHS_RU.index(month) + 1,
                                "is_make_operations": True,
                                "bank_out": 5,
                                "date_start": datetime.datetime(
                                    year_now, MONTHS_RU.index(month) + 1, 1
                                ),
                                "operation_id": 0,
                                "type_operations": "SubcontractOtherCategory",
                                "id_groupe": category.id,
                                "expected": 0,
                            }

                # Добавляем месяцы для итогов arr_out
                arr_out["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

        # Добавляем сервисы в "другое" для arr_out, исключая SEO

        for service in services:
            if service.name != "SEO":  # Пропускаем SEO
                name = f"{service.name}({service.name_long_ru})"
                arr_out["category"][0]["group"]["остальное"][name] = {}
                for i, month in enumerate(months_current_year):
                    arr_out["category"][0]["group"]["остальное"][name][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

        # распределение операций
        for operation in operations:
            month_name = MONTHS_RU[operation.data.month - 1]
            prev_month = (
                MONTHS_RU[operation.data.month] if operation.data.month < 12 else None
            )
            is_prev_month = prev_month in months_current_year if prev_month else False

            # операции ВНУТРЕННИЕ СЧЕТА
            if operation.operaccount:
                id_operacc_categ = get_id_categ_oper(operation.operaccount.category)
                arr_inside_all["category"][2]["group"][id_operacc_categ][month_name][
                    "amount_month"
                ] += operation.amount
                arr_inside_all["category"][2]["total"]["total"][month_name][
                    "amount_month"
                ] += operation.amount

                arr_inside_all["total_category"]["total"][month_name][
                    "amount_month"
                ] += operation.amount
            elif operation.salary and operation.employee:
                pass
                # 10 число в след месяц
                if operation.salary.id == 1:
                    month_name = MONTHS_RU[operation.data.month - 2]
                    if month_name in arr_inside_all["category"][1]["total"]["total"]:
                        arr_inside_all["category"][1]["total"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_inside_all["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

                # не 10 число обычно
                else:
                    arr_inside_all["category"][1]["total"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                    arr_inside_all["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
            elif operation.nalog:

                if operation.nalog.id != 4 and operation.nalog.id != 9:

                    arr_inside_all["category"][0]["group"]["ИТОГО налоги с ЗП:"][
                        month_name
                    ]["amount_month"] += operation.amount
                    arr_inside_all["category"][0]["total"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                    arr_inside_all["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                elif operation.nalog.id == 4:

                    arr_inside_all["category"][0]["total"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                    arr_inside_all["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                elif operation.nalog.id == 9:

                    arr_in_out_after_all_total["category"][1]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                    arr_in_out_after_all_total["category"][1]["total"][month_name][
                        "operation_id"
                    ] = operation.id

            # операции прихода по договорам услуг
            elif operation.monthly_bill and operation.suborder is None:
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
                print("operation.suborder",operation)
                
                # расходы по договорам услуг
                # Для SEO
                if operation.suborder.month_bill.service.name == "SEO":

                    if (
                        operation.suborder.category_employee
                        and operation.suborder.category_employee.name == "ИП Галаев"
                    ):
                        print("operation.suborder.category_employee",operation)
                        arr_out["category"][0]["group"]["SEO"]["ИП Галаев"][month_name][
                            "amount_month"
                        ] += operation.amount
                    else:
                        arr_out["category"][0]["group"]["SEO"]["Другое"][month_name][
                            "amount_month"
                        ] += operation.amount

                # Для других субподрядов
                else:

                    service_name = f"{operation.suborder.month_bill.service.name}({operation.suborder.month_bill.service.name_long_ru})"
                    if service_name in arr_out["category"][0]["group"]["остальное"]:
                        arr_out["category"][0]["group"]["остальное"][service_name][
                            month_name
                        ]["amount_month"] += operation.amount
                        arr_out["category"][0]["group"]["остальное"][service_name][
                            month_name
                        ]["operation_id"] = operation.id
                # Добавляем в общий итог по месяцу операции
                arr_out["total_category"]["total"][month_name][
                    "amount_month"
                ] += operation.amount

            elif operation.suborder_other:
                # # Добавляем в общий итог по месяцу операции
                arr_out["total_category"]["total"][month_name][
                    "amount_month"
                ] += operation.amount
                if operation.suborder_other.name == "Topvisor":
                    arr_out["category"][0]["group"]["SEO"]["Topvisor"][month_name][
                        "amount_month"
                    ] += operation.amount
                    arr_out["category"][0]["group"]["SEO"]["Topvisor"][month_name][
                        "operation_id"
                    ] = operation.id
                    if is_prev_month:
                        arr_out["category"][0]["group"]["SEO"]["Topvisor"][prev_month][
                            "expected"
                        ] += operation.amount

                else:
                    service_name = operation.suborder_other.name
                    arr_out["category"][2]["group"][service_name][month_name][
                        "amount_month"
                    ] += operation.amount
                    arr_out["category"][2]["group"][service_name][month_name][
                        "operation_id"
                    ] = operation.id
                    if is_prev_month:
                        arr_out["category"][2]["group"][service_name][prev_month][
                            "expected"
                        ] += operation.amount
            # операции между счетами
            elif operation.between_bank:
                if operation.bank_in == bank:
                    if (
                        operation.between_bank.name
                        == "перевод на ИП для оплаты субподряда"
                    ):
                        arr_out["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_out["category"][1]["group"][
                            "перевод на ИП для оплаты субподряда"
                        ][month_name]["amount_month"] += operation.amount
                        arr_out["category"][1]["group"][
                            "перевод на ИП для оплаты субподряда"
                        ][month_name]["operation_id"] = operation.id

                        if is_prev_month:
                            arr_out["category"][1]["group"][
                                "перевод на ИП для оплаты субподряда"
                            ][prev_month]["expected"] += operation.amount
                    elif operation.between_bank.name == "ПРЕМИИ":

                        name_to_find = "ПРЕМИИ"
                        item = next(
                            (
                                x
                                for x in arr_in_out_all["category"]
                                if x["name"] == name_to_find
                            ),
                            None,
                        )
                        if item:
                            item["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            item["total"][month_name]["operation_id"] = operation.id
                            if is_prev_month:
                                item["total"][prev_month]["expected"] += operation.amount
                    elif (
                        operation.between_bank.name
                        == "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП"
                    ):
                        name_to_find = "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП"
                        item = next(
                            (
                                x
                                for x in arr_in_out_after_all_total["category"]
                                if x["name"] == name_to_find
                            ),
                            None,
                        )
                        if item:
                            item["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            item["total"][month_name]["operation_id"] = operation.id
                    elif operation.between_bank.name == "ПРИБЫЛЬ 1% ЦРП 5%":
                        name_to_find = "ПРИБЫЛЬ 1% ЦРП 5%"

                        item = next(
                            (
                                x
                                for x in arr_in_out_all["category"]
                                if x["name"] == name_to_find
                            ),
                            None,
                        )
                        if item:
                            item["total"][month_name][
                                "amount_month_chek"
                            ] += operation.amount
                            item["total"][month_name]["operation_id"] = operation.id
                            item["total"][month_name]["chek"] = True
                            if is_prev_month:
                                item["total"][prev_month]["expected"] = item["total"][month_name]["percent"]
                                
                    elif operation.between_bank.name == "КВ 20% ЦРП 50%":
                        name_to_find = "КВ 20% ЦРП 50%"

                        item = next(
                            (
                                x
                                for x in arr_in_out_all["category"]
                                if x["name"] == name_to_find
                            ),
                            None,
                        )
                        if item:
                            item["total"][month_name][
                                "amount_month_chek"
                            ] += operation.amount
                            item["total"][month_name]["operation_id"] = operation.id
                            item["total"][month_name]["chek"] = True
                            if is_prev_month:
                                item["total"][prev_month]["expected"] = item["total"][month_name]["percent"]
                                
                elif operation.bank_to == bank:
                    arr_in["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                    if operation.between_bank.name == "зачисление на ООО":
                        arr_in["category"][1]["group"]["зачисление из хранилища"][
                            month_name
                        ]["operation_id"] = operation.id
                        arr_in["category"][1]["group"]["зачисление из хранилища"][
                            month_name
                        ]["amount_month"] += operation.amount

                        # name_to_find = "зачисление из хранилища"
                        # item = next(
                        #     (
                        #         x
                        #         for x in arr_in["category"][1]["group"]
                        #         if x == name_to_find
                        #     ),
                        #     None,
                        # )
                        # if item:
                        #     item["total"][month_name][
                        #         "amount_month"
                        #     ] += operation.amount
                        #     item["total"][month_name]["operation_id"] = operation.id

            else:
                # операции между счетами
                # операции расход
                if operation.bank_in == bank:
                    arr_out["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                    if operation.bank_to.id == 2:
                        arr_out["category"][1]["group"][
                            "перевод на ИП для оплаты субподряда"
                        ][month_name]["amount_month"] += operation.amount
                        arr_out["category"][1]["group"][
                            "перевод на ИП для оплаты субподряда"
                        ][month_name]["operation_id"] = operation.id

                        if is_prev_month:
                            arr_out["category"][1]["group"][
                                "перевод на ИП для оплаты субподряда"
                            ][prev_month]["expected"] += operation.amount
                # операции доход:
                else:
                    pass

        # разные общие суммы
        for i, month in enumerate(months_current_year):
            # === Расчет "РЕАЛЬНЫЕ ПОСТУПЛЕНИЯ ООО (ВЫРУЧКА-СУБПОДРЯД И БУХ)" ===
            in_sum = (
                arr_in["total_category"]["total"].get(month, {}).get("amount_month", 0)
            )
            out_sum = (
                arr_out["total_category"]["total"].get(month, {}).get("amount_month", 0)
            )

            if month not in arr_in_out_all["category"][0]["total"]:
                arr_in_out_all["category"][0]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
            diff_in_out = in_sum - out_sum
            arr_in_out_all["category"][0]["total"][month]["amount_month"] = diff_in_out

            # ПРИБЫЛЬ 1% ЦРП 5%
            if arr_in_out_all["category"][1]["total"][month]["chek"] == True:

                in_out_all_crp = arr_in_out_all["category"][1]["total"][month][
                    "amount_month_chek"
                ]
            else:
                in_out_all_crp = (
                    diff_in_out
                    * arr_in_out_all["category"][1]["total"][month]["percent"]
                    / 100
                )
            arr_in_out_all["category"][1]["total"][month][
                "amount_month"
            ] = in_out_all_crp

            # КВ 20% ЦРП 50%
            if arr_in_out_all["category"][2]["total"][month]["chek"] == True:

                in_out_all_crp_kv = arr_in_out_all["category"][2]["total"][month][
                    "amount_month_chek"
                ]

            else:
                in_out_all_crp_kv = (
                    diff_in_out
                    * arr_in_out_all["category"][2]["total"][month]["percent"]
                    / 100
                )
            arr_in_out_all["category"][2]["total"][month][
                "amount_month"
            ] = in_out_all_crp_kv

            # ИТОГО  РЕАЛЬНЫЕ ПОСТУПЛЕНИЯ ООО (ВЫРУЧКА-СУБПОДРЯД И БУХ)
            in_out_all_total = (
                in_out_all_crp
                + in_out_all_crp_kv
                + arr_in_out_all["category"][3]["total"][month]["amount_month"]
            )
            arr_in_out_all["category"][4]["total"][month][
                "amount_month"
            ] = in_out_all_total

            # ДОХОД - РЕАЛЬНЫЙ РАСХОД в текущем месяце
            all_out_dop = arr_inside_all["total_category"]["total"][month][
                "amount_month"
            ]

            diff_in_out_real = in_sum - out_sum - all_out_dop - in_out_all_total
            arr_in_out_after_all["category"][0]["total"][month][
                "amount_month"
            ] = diff_in_out_real

            # НАЛОГ УСН ООО доход-расходы*15% ЦРП 2- ТРП 1,5% (отложенные на выплату)
            ycno = (
                in_sum
                * arr_in_out_after_all["category"][1]["total"][month]["percent"]
                / 100
            )
            
            arr_in_out_after_all["category"][1]["total"][month]["amount_month"] = ycno

            # Реальный налог УСН с ООО доход - 1%
            arr_in_out_after_all["category"][2]["total"][month]["amount_month"] = (
                in_sum
                * arr_in_out_after_all["category"][2]["total"][month]["percent"]
                / 100
            )

            # ПРОВЕРКА ДОХОД - РАСХОД
            arr_in_out_after_all["category"][3]["total"][month]["amount_month"] = (
                diff_in_out_real - ycno
            )

            # ПРОВЕРКА ООО ДОХОД-РАСХОД = ОСТАТОК из первого общего блока
            arr_in_out_all["category"][5]["total"][month]["amount_month"] = (
                diff_in_out_real - ycno
            )

            # ДОХОД-РАСХОД (в текущем месяце без УСН и вывода остатков)
            arr_in_out_after_all_total["category"][0]["total"][month][
                "amount_month"
            ] = diff_in_out_real

            # ОСТАТОК на Р/С на конец месяца (после уплаты УСН и вывода остатков)
            nalog_ycn = arr_in_out_after_all_total["category"][1]["total"][month][
                "amount_month"
            ]
            to_ip = arr_in_out_after_all_total["category"][2]["total"][month][
                "amount_month"
            ]

            for i, month in enumerate(months_current_year):
                if i + 1 < len(months_current_year):
                    month_prev = months_current_year[i + 1]
                    
                    prev_all_sum_month = arr_in_out_after_all_total["category"][3][
                        "total"
                    ][month_prev]["amount_month"]
                    arr_in_out_after_all["category"][1]["total"][month]["expected"] = arr_in_out_after_all["category"][1]["total"][month_prev]["percent"]
                    arr_in_out_after_all["category"][2]["total"][month]["expected"] = arr_in_out_after_all["category"][2]["total"][month_prev]["percent"]
                
                else:
                    # Для самого последнего месяца (например, "Январь") — остаток на конец декабря прошлого года, если есть
                    prev_all_sum_month = 0
                    if old_oper_arr:
                        prev_year = year_now - 1

                        last_month = "Декабрь"
                        prev_year_data = old_oper_arr.get(prev_year)
                        if prev_year_data:
                            try:

                                category_list = prev_year_data[
                                    "arr_in_out_after_all_total"
                                ]["category"]
                                prev_all_sum_month = category_list[3]["total"][
                                    last_month
                                ]["amount_month"]
                            except Exception as e:
                                print(
                                    "Ошибка при доступе к остатку прошлого года (old_oper_arr):",
                                    e,
                                )
                                prev_all_sum_month = 0

                all_sum_month = (
                    diff_in_out_real - nalog_ycn - to_ip + prev_all_sum_month
                )
                arr_in_out_after_all_total["category"][3]["total"][month][
                    "amount_month"
                ] = all_sum_month

            # for i, month in enumerate(months_current_year):
            #     if i + 1 < len(months_current_year):
            #         month_prev = months_current_year[i + 1]
            #         prev_all_sum_month = arr_in_out_after_all_total["category"][3]["total"][month_prev]["amount_month"]
            #     else:
            #         prev_all_sum_month = 0

            #     all_sum_month = diff_in_out_real - nalog_ycn - to_ip + prev_all_sum_month
            #     arr_in_out_after_all_total["category"][3]["total"][month]["amount_month"] = all_sum_month

            # Р/С на начало месяца
            # получить следующий месяц
            for i, month in enumerate(months_current_year):
                if i == len(months_current_year) - 1:
                    # Для самого последнего месяца (например, "Январь") — остаток на конец декабря прошлого года, если есть
                    last_balance = 0
                    if old_oper_arr:
                        prev_year = year_now - 1
                        last_month = "Декабрь"
                        prev_year_data = old_oper_arr.get(prev_year)
                        if prev_year_data:
                            try:
                                category_list = prev_year_data[
                                    "arr_in_out_after_all_total"
                                ]["category"]
                                last_balance = category_list[3]["total"][last_month][
                                    "amount_month"
                                ]
                            except Exception as e:
                                print(
                                    "Ошибка при доступе к остатку прошлого года (old_oper_arr):",
                                    e,
                                )
                                last_balance = 0
                    arr_start_month["total"][month]["amount_month"] = last_balance
                else:
                    next_month = months_current_year[i + 1]
                    arr_start_month["total"][month]["amount_month"] = (
                        arr_in_out_after_all_total["category"][3]["total"][next_month][
                            "amount_month"
                        ]
                    )

        return (
            arr_in,
            arr_out,
            arr_in_out_all,
            arr_inside_all,
            arr_in_out_after_all,
            arr_in_out_after_all_total,
            arr_start_month,
        )


def fill_operations_arrays_ip(
    categ_percent_by_name,
    categ_percent_list,
    services,
    other_categ_subkontract,
    arr_start_month,
    arr_inside_all,
    arr_out,
    arr_in_out_all,
    arr_in,
    arr_in_out_after_all,
    arr_summ_to_persent,
    arr_keep_ip,
    arr_end_month_ip,
    CATEGORY_OPERACCOUNT,
    months_current_year,
    month_numbers,
    year_now,
    operations,
    bank,
    arr_real_diff,
    context_ooo,
    cate_oper_beetwen_by_name,
    categoru_nalog,
    is_old_oper,
    old_oper_arr,
):
    categoru_nalog_fact = categoru_nalog.get(name="ФАКТИЧЕСКАЯ ОПЛАТА НАЛОГОВ")

    between_id_ip_to_mir = cate_oper_beetwen_by_name.get(
        "вывод $ для оплаты субподряда (вручную)"
    )
    between_id_for_ooo_ip_to_storage = cate_oper_beetwen_by_name.get(
        "вывод остатков ООО в Хранилище"
    )
    between_id_for_ooo_ip_to_storage_crp = cate_oper_beetwen_by_name.get(
        "остаток ПРИБЫЛЬ 1% ЦРП 5%"
    )
    between_id_for_ooo_ip_to_storage_kv = cate_oper_beetwen_by_name.get(
        "остаток КВ 0,5 % ЦРП 50%"
    )
    between_id_for_ip_to_storage_bonus = cate_oper_beetwen_by_name.get(
        "ПРЕМИИ"
    )

    categ_percent_crp = categ_percent_by_name.get("ПРИБЫЛЬ 1% ЦРП 5%")
    categ_percent_crp_kv = categ_percent_by_name.get("КВ 20% ЦРП 50%")
    categ_percent_to_boss = categ_percent_by_name.get(
        "на квартальную премию собственникам"
    )
    categ_percent_to_boss2 = categ_percent_by_name.get("компенсация владельцу с ИП")

    if is_old_oper:

        def reverse_months_in_dict(d):
            if isinstance(d, dict):
                months = [m for m in MONTHS_RU if m in d]
                if len(months) == 12 and set(months) == set(MONTHS_RU):
                    # Это словарь месяцев, разворачиваем в прямой порядок (январь → декабрь)
                    items = [(m, d[m]) for m in MONTHS_RU if m in d]
                    return {k: reverse_months_in_dict(v) for k, v in items}
                else:
                    return {k: reverse_months_in_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [reverse_months_in_dict(x) for x in d]
            else:
                return d

        # Группировка операций по годам
        operations_by_year = {}
        # Получаем уникальные года из операций
        years = set()

        for operation in operations:
            years.add(operation.data.year)

        for year in sorted(years):
            # Фильтруем операции за этот год
            operations_year = [op for op in operations if op.data.year == year]
            # Копируем структуры для этого года
            arr_start_month_y = copy.deepcopy(arr_start_month)
            arr_in_y = copy.deepcopy(arr_in)
            arr_out_y = copy.deepcopy(arr_out)
            arr_in_out_all_y = copy.deepcopy(arr_in_out_all)
            arr_real_diff_y = copy.deepcopy(arr_real_diff)
            arr_inside_all_y = copy.deepcopy(arr_inside_all)
            arr_in_out_after_all_y = copy.deepcopy(arr_in_out_after_all)
            arr_summ_to_persent_y = copy.deepcopy(arr_summ_to_persent)
            arr_keep_y = copy.deepcopy(arr_keep_ip)
            arr_end_month_y = copy.deepcopy(arr_end_month_ip)

            # months_current_year для этого года
            months_year = [MONTHS_RU[month - 1] for month in range(1, 13)]
            months_year.reverse()
            month_numbers_year = {month: i + 1 for i, month in enumerate(months_year)}

            # --- ОСНОВНОЙ КОД ОБРАБОТКИ ДЛЯ КАЖДОГО ГОДА ---
            # Добавляем категории из CATEGORY_OPERACCOUNT
            for categ_oper in CATEGORY_OPERACCOUNT:

                arr_inside_all_y["category"][1]["group"][categ_oper[1]] = {}
                # Добавляем месяцы для каждой категории
                for i, month in enumerate(months_year):
                    month_number = month_numbers_year[month]
                    arr_inside_all_y["category"][1]["group"][categ_oper[1]][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

            # Добавляем месяцы
            for i, month in enumerate(months_year):
                month_number = month_numbers_year[month]
                # рс на анчало меясца
                arr_start_month_y["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                # рс на конец меясца
                arr_end_month_y["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }

                # СУБПОДРЯДЧИКИ + ПЛОЩАДКИ, в т.ч.
                arr_out_y["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": f"{month_number:02d}",
                    "is_make_operations": False,
                }
                arr_out_y["category"][1]["group"][
                    "вывод $ для оплаты субподряда (вручную)"
                ][month] = {
                    "is_make_operations": True,
                    "bank_out": between_id_ip_to_mir["bank_to"],
                    "date_start": datetime.datetime(
                        year, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "type_operations": "between",
                    "between_id": between_id_ip_to_mir["id"],
                    "amount_month": 0,
                    "expected": 0,
                }
                arr_out_y["category"][1]["group"]["вывод остатков ООО в Хранилище"][
                    month
                ] = {
                    "is_make_operations": True,
                    "bank_out": between_id_for_ooo_ip_to_storage["bank_to"],
                    "date_start": datetime.datetime(
                        year, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "type_operations": "between",
                    "between_id": between_id_for_ooo_ip_to_storage["id"],
                    "amount_month": 0,
                    "expected": 0,
                }

                # первый блок доход расход
                for in_out in arr_in_out_all_y["category"]:

                    in_out["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    if in_out["name"] == "ПРИБЫЛЬ 1% ЦРП 5%":
                        in_out["total"][month]["is_make_operations"] = True
                        in_out["total"][month]["type_operations"] = "percent"

                        in_out["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        in_out["total"][month]["id_groupe"] = categ_percent_crp["id"]

                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_crp["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        in_out["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        in_out["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )

                    elif in_out["name"] == "КВ 20% ЦРП 50%":
                        in_out["total"][month]["is_make_operations"] = True
                        in_out["total"][month]["type_operations"] = "percent"

                        in_out["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        in_out["total"][month]["id_groupe"] = categ_percent_crp_kv["id"]

                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_crp_kv["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        in_out["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        in_out["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )
                # второй  блок доход расход
                for in_out_after in arr_in_out_after_all_y["category"]:
                    in_out_after["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    if in_out_after["name"] == "ФАКТИЧЕСКАЯ ОПЛАТА НАЛОГОВ":
                        in_out_after["total"][month]["is_make_operations"] = True
                        in_out_after["total"][month]["bank_out"] = 5
                        in_out_after["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        in_out_after["total"][month]["operation_id"] = 0
                        in_out_after["total"][month]["type_operations"] = "nalog"
                        in_out_after["total"][month]["id_groupe"] = categoru_nalog_fact[
                            "id"
                        ]

                # В ХРАНИЛИЩЕ:
                arr_keep_y["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                for keep_ip in arr_keep_y["category"]:
                    if keep_ip["name"] == "остаток ПРИБЫЛЬ 1% ЦРП 5%":
                        keep_ip["total"][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                        }
                        keep_ip["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        keep_ip["total"][month]["is_make_operations"] = True

                        keep_ip["total"][month]["bank_out"] = (
                            between_id_for_ooo_ip_to_storage_crp["bank_to"]
                        )
                        keep_ip["total"][month]["operation_id"] = 0
                        keep_ip["total"][month]["type_operations"] = "between"
                        keep_ip["total"][month]["between_id"] = (
                            between_id_for_ooo_ip_to_storage_crp["id"]
                        )
                        keep_ip["total"][month]["amount_month_chek"] = 0
                        keep_ip["total"][month]["chek"] = False
                    elif keep_ip["name"] == "остаток КВ 0,5 % ЦРП 50%":
                        keep_ip["total"][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                        }
                        keep_ip["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        keep_ip["total"][month]["is_make_operations"] = True

                        keep_ip["total"][month]["bank_out"] = (
                            between_id_for_ooo_ip_to_storage_kv["bank_to"]
                        )
                        keep_ip["total"][month]["operation_id"] = 0
                        keep_ip["total"][month]["type_operations"] = "between"
                        keep_ip["total"][month]["between_id"] = (
                            between_id_for_ooo_ip_to_storage_kv["id"]
                        )
                        keep_ip["total"][month]["amount_month_chek"] = 0
                        keep_ip["total"][month]["chek"] = False
                    elif keep_ip["name"] == "вывод остатков ООО в Хранилище":
                        keep_ip["total"][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                        }
                        keep_ip["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        keep_ip["total"][month]["is_make_operations"] = True

                        keep_ip["total"][month]["bank_out"] = (
                            between_id_for_ooo_ip_to_storage_kv["bank_to"]
                        )
                        keep_ip["total"][month]["operation_id"] = 0
                        keep_ip["total"][month]["type_operations"] = "between"
                        keep_ip["total"][month]["between_id"] = (
                            between_id_for_ooo_ip_to_storage_kv["id"]
                        )
                        keep_ip["total"][month]["amount_month_chek"] = 0
                        keep_ip["total"][month]["chek"] = False

                for summ_to_persent in arr_summ_to_persent_y["category"]:
                    summ_to_persent["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    if summ_to_persent["name"] == "на квартальную премию собственникам":
                        summ_to_persent["total"][month]["is_make_operations"] = True
                        summ_to_persent["total"][month]["type_operations"] = "percent"

                        summ_to_persent["total"][month]["date_start"] = (
                            datetime.datetime(year, MONTHS_RU.index(month) + 1, 1)
                        )
                        summ_to_persent["total"][month]["id_groupe"] = (
                            categ_percent_to_boss["id"]
                        )
                        summ_to_persent["total"][month]["between_id"] = (
                            categ_percent_to_boss["category_between"]
                        )
                        summ_to_persent["total"][month]["bank_out"] = (
                            categ_percent_to_boss["category_between__bank_to"]
                        )
                        summ_to_persent["total"][month]["amount_month_chek"] = 0
                        summ_to_persent["total"][month]["chek"] = False

                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_to_boss["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        summ_to_persent["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        summ_to_persent["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )

                    elif summ_to_persent["name"] == "компенсация владельцу с ИП":
                        summ_to_persent["total"][month]["is_make_operations"] = True
                        summ_to_persent["total"][month]["type_operations"] = "percent"

                        summ_to_persent["total"][month]["date_start"] = (
                            datetime.datetime(year, MONTHS_RU.index(month) + 1, 1)
                        )
                        summ_to_persent["total"][month]["id_groupe"] = (
                            categ_percent_to_boss2["id"]
                        )
                        summ_to_persent["total"][month]["between_id"] = (
                            categ_percent_to_boss2["category_between"]
                        )
                        summ_to_persent["total"][month]["bank_out"] = (
                            categ_percent_to_boss2["category_between__bank_to"]
                        )
                        summ_to_persent["total"][month]["amount_month_chek"] = 0
                        summ_to_persent["total"][month]["chek"] = False

                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_to_boss2["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        summ_to_persent["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        summ_to_persent["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )

                # внутренние счета расходы все
                arr_inside_all_y["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }

                for inside_all in arr_inside_all_y["category"]:
                    inside_all["total"]["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    if inside_all["name"] == "НАЛОГИ ИП (откладываем до оплаты):":
                        inside_all["group"]["ИТОГО налоги на ИП"][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                        }

            for service in services:
                name = f"{service.name}({service.name_long_ru})"
                arr_in_y["category"][0]["group"][name] = {}

                for i, month in enumerate(months_year):
                    month_number = month_numbers_year[month]

                    # Для услуг
                    arr_in_y["category"][0]["group"][name][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

                    # Для переводов с ооо
                    arr_in_y["category"][1]["group"]["на премии"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }
                    arr_in_y["category"][1]["group"]["ООО прибыль ЦРП 5%"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }
                    # Для переводов с ооо
                    arr_in_y["category"][1]["group"][
                        "перевод с ООО для оплаты субподряда"
                    ][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }
                    arr_in_y["category"][1]["group"][
                        "зачисление $ для оплаты субподряда"
                    ][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }
                    arr_in_y["category"][1]["group"]["зачисление из хранилища"][
                        month
                    ] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }
                    # Для переводов с ооо
                    arr_in_y["category"][1]["group"]["ПЕРЕВОД ОСТАТКОВ С ООО"][
                        month
                    ] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

                    # Для итогов
                    arr_in_y["total_category"]["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

                    # Для arr_out
                    # Добавляем месяцы для других субподрядов
                    for category in other_categ_subkontract:

                        if category.name not in arr_out_y["category"][2]["group"]:
                            arr_out_y["category"][2]["group"][category.name] = {}
                            # Инициализируем месяцы для каждой категории
                            for i, month in enumerate(months_year):
                                month_number = month_numbers_year[month]
                                arr_out_y["category"][2]["group"][category.name][
                                    month
                                ] = {
                                    "amount_month": 0,
                                    "month_number": MONTHS_RU.index(month) + 1,
                                    "is_make_operations": True,
                                    "bank_out": 5,
                                    "date_start": datetime.datetime(
                                        year, MONTHS_RU.index(month) + 1, 1
                                    ),
                                    "operation_id": 0,
                                    "type_operations": "SubcontractOtherCategory",
                                    "id_groupe": category.id,
                                    "expected": 0,
                                }

                    arr_out_y["category"][0]["group"][name] = {}
                    for i, month in enumerate(months_year):
                        arr_out_y["category"][0]["group"][name][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                            "is_make_operations": False,
                        }

                    # Добавляем месяцы для итогов arr_out
                    arr_out_y["total_category"]["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

            # распределение операций
            for operation in operations_year:
                month_name = MONTHS_RU[operation.data.month - 1]
                prev_month = (
                    MONTHS_RU[operation.data.month]
                    if operation.data.month < 12
                    else None
                )
                is_prev_month = prev_month in months_year if prev_month else False

                # операции ВНУТРЕННИЕ СЧЕТА
                if operation.operaccount:
                    id_operacc_categ = get_id_categ_oper(operation.operaccount.category)
                    arr_inside_all_y["category"][1]["group"][id_operacc_categ][
                        month_name
                    ]["amount_month"] += operation.amount
                    arr_inside_all_y["category"][1]["total"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                    arr_inside_all_y["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                # операции налоги
                elif operation.nalog:
                    if operation.nalog.id != 10:
                        arr_inside_all_y["category"][0]["total"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

                        arr_inside_all_y["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                    else:
                        arr_in_out_after_all_y["category"][2]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

                        arr_in_out_after_all_y["category"][2]["total"][month_name][
                            "operation_id"
                        ] = operation.id
                # операции прихода по договорам услуг
                elif operation.monthly_bill and operation.suborder is None:
                    # поступления по договорам услуг

                    service_name = f"{operation.monthly_bill.service.name}({operation.monthly_bill.service.name_long_ru})"

                    if service_name in arr_in_y["category"][0]["group"]:
                        arr_in_y["category"][0]["group"][service_name][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_in_y["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

                # операции расхода по договорам услуг
                elif operation.suborder:
                    service_name = f"{operation.suborder.month_bill.service.name}({operation.suborder.month_bill.service.name_long_ru})"
                    if service_name in arr_out_y["category"][0]["group"]:
                        arr_out_y["category"][0]["group"][service_name][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_out_y["category"][0]["group"][service_name][month_name][
                            "operation_id"
                        ] = operation.id

                    # Добавляем в общий итог по месяцу операции
                    arr_out_y["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                elif operation.suborder_other:
                    # # Добавляем в общий итог по месяцу операции
                    arr_out_y["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                    service_name = operation.suborder_other.name
                    arr_out_y["category"][2]["group"][service_name][month_name][
                        "amount_month"
                    ] += operation.amount
                    arr_out_y["category"][2]["group"][service_name][month_name][
                        "operation_id"
                    ] = operation.id
                    if is_prev_month:
                        arr_out_y["category"][2]["group"][service_name][prev_month][
                            "expected"
                        ] += operation.amount

                elif operation.between_bank:
                    # исходящее между счетами
                    if operation.bank_in == bank:
                        if (
                            operation.between_bank.name
                            == "вывод $ для оплаты субподряда (вручную)"
                        ):
                            arr_out_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "вывод $ для оплаты субподряда (вручную)"
                            ][month_name]["amount_month"] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "вывод $ для оплаты субподряда (вручную)"
                            ][month_name]["operation_id"] = operation.id

                            if is_prev_month:
                                arr_out_y["category"][1]["group"][
                                    "вывод $ для оплаты субподряда (вручную)"
                                ][prev_month]["expected"] += operation.amount
                        elif (
                            operation.between_bank.name
                            == "вывод остатков ООО в Хранилище"
                        ):
                            arr_out_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "вывод остатков ООО в Хранилище"
                            ][month_name]["amount_month"] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "вывод остатков ООО в Хранилище"
                            ][month_name]["operation_id"] = operation.id

                            arr_keep_y["category"][2]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_keep_y["category"][2]["total"][month_name][
                                "operation_id"
                            ] = operation.id
                            arr_keep_y["category"][2]["total"][month_name][
                                "chek"
                            ] = True

                        elif operation.between_bank.name == "остаток ПРИБЫЛЬ 1% ЦРП 5%":
                            pass
                            arr_keep_y["category"][0]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_keep_y["category"][0]["total"][month_name][
                                "operation_id"
                            ] = operation.id
                            arr_keep_y["category"][0]["total"][month_name][
                                "chek"
                            ] = True

                        elif operation.between_bank.name == "остаток КВ 0,5 % ЦРП 50%":
                            pass
                            arr_keep_y["category"][1]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_keep_y["category"][1]["total"][month_name][
                                "operation_id"
                            ] = operation.id
                            arr_keep_y["category"][1]["total"][month_name][
                                "chek"
                            ] = True

                        elif (
                            operation.between_bank.name
                            == "на квартальную премию собственникам"
                        ):

                            name_to_find = "на квартальную премию собственникам"
                            item = next(
                                (
                                    x
                                    for x in arr_summ_to_persent_y["category"]
                                    if x["name"] == name_to_find
                                ),
                                None,
                            )
                            if item:
                                item["total"][month_name][
                                    "amount_month_chek"
                                ] += operation.amount
                                item["total"][month_name]["operation_id"] = operation.id
                                item["total"][month_name]["chek"] = True

                        elif (
                            operation.between_bank.name == "компенсация владельцу с ИП"
                        ):

                            name_to_find = "компенсация владельцу с ИП"
                            item = next(
                                (
                                    x
                                    for x in arr_summ_to_persent_y["category"]
                                    if x["name"] == name_to_find
                                ),
                                None,
                            )
                            if item:
                                item["total"][month_name][
                                    "amount_month_chek"
                                ] += operation.amount
                                item["total"][month_name]["operation_id"] = operation.id
                                item["total"][month_name]["chek"] = True

                    # приходящее между счетами
                    if operation.bank_to == bank:
                        if (
                            operation.between_bank.name
                            == "перевод на ИП для оплаты субподряда"
                        ):
                            arr_in_y["category"][1]["group"][
                                "перевод с ООО для оплаты субподряда"
                            ][month_name]["amount_month"] += operation.amount
                            arr_in_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                        elif (
                            operation.between_bank.name
                            == "зачисление на ИП для оплаты субподряда"
                        ):
                            arr_in_y["category"][1]["group"][
                                "зачисление $ для оплаты субподряда"
                            ][month_name]["amount_month"] += operation.amount
                            arr_in_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                        elif operation.between_bank.name == "зачисление на ИП":
                            arr_in_y["category"][1]["group"]["зачисление из хранилища"][
                                month_name
                            ]["amount_month"] += operation.amount
                            arr_in_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount

                        elif operation.between_bank.name == "ПРЕМИИ":
                            arr_in_y["category"][1]["group"]["на премии"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_in_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount

                            arr_in_out_all_y["category"][2]["total"][month_name][
                                "amount_month"
                            ] += operation.amount

                        elif (
                            operation.between_bank.name
                            == "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП"
                        ):
                            arr_in_y["category"][1]["group"]["ПЕРЕВОД ОСТАТКОВ С ООО"][
                                month_name
                            ]["amount_month"] += operation.amount
                            arr_in_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount

                            #
                # данные из кеша других страниц

            # данные из кеша других страниц
            if context_ooo and isinstance(context_ooo, dict):
                for key, value in context_ooo.items():

                    # --- Обработка arr_in_out_all из кеша ---
                    if key == "arr_in_out_all":
                        arr_in_out_all_ooo = value
                        for category in arr_in_out_all_ooo.get("category", []):
                            if category.get("name") == "ПРИБЫЛЬ 1% ЦРП 5%":
                                total = category.get("total", {})
                                for month_name, month_data in total.items():
                                    if month_data.get("chek") is True:
                                        v = month_data.get("amount_month_chek", 0)

                                    else:
                                        v = month_data.get("amount_month", 0)

                                    # Безопасная инициализация и прибавление
                                    group = arr_in_y["category"][1]["group"]
                                    group.setdefault("ООО прибыль ЦРП 5%", {})
                                    group["ООО прибыль ЦРП 5%"].setdefault(
                                        month_name, {}
                                    )
                                    group["ООО прибыль ЦРП 5%"][month_name].setdefault(
                                        "amount_month", 0
                                    )
                                    group["ООО прибыль ЦРП 5%"][month_name][
                                        "amount_month"
                                    ] += v

                                    # Аналогично для total_category
                                    total_cat = arr_in_y["total_category"]["total"]
                                    total_cat.setdefault(month_name, {})
                                    total_cat[month_name].setdefault("amount_month", 0)
                                    total_cat[month_name]["amount_month"] += v
                            elif category.get("name") == "КВ 20% ЦРП 50%":
                                total = category.get("total", {})
                                for month_name, month_data in total.items():
                                    if month_data.get("chek") is True:
                                        v = month_data.get("amount_month_chek", 0)

                                    else:
                                        v = month_data.get("amount_month", 0)

                                    # Безопасная инициализация и прибавление
                                    group = arr_in_y["category"][1]["group"]
                                    group.setdefault("ООО КВ ЦРП 50%", {})
                                    group["ООО КВ ЦРП 50%"].setdefault(month_name, {})
                                    group["ООО КВ ЦРП 50%"][month_name].setdefault(
                                        "amount_month", 0
                                    )
                                    group["ООО КВ ЦРП 50%"][month_name][
                                        "amount_month"
                                    ] += v

                                    # Аналогично для total_category
                                    total_cat = arr_in_y["total_category"]["total"]
                                    total_cat.setdefault(month_name, {})
                                    total_cat[month_name].setdefault("amount_month", 0)
                                    total_cat[month_name]["amount_month"] += v

            # разные общие суммы
            for i, month in enumerate(months_year):
                # === РЕАЛЬНЫЕ ПОСТУПЛЕНИЯ ИП (ВЫРУЧКА-СУБПОДРЯД)" ===
                in_sum = (
                    arr_in_y["total_category"]["total"]
                    .get(month, {})
                    .get("amount_month", 0)
                )
                out_sum = (
                    arr_out_y["total_category"]["total"]
                    .get(month, {})
                    .get("amount_month", 0)
                )
                if month not in arr_real_diff_y["total"]:
                    arr_real_diff_y["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                diff_in_out = in_sum - out_sum
                arr_real_diff_y["total"][month]["amount_month"] = diff_in_out
                # # ПРИБЫЛЬ 1% ЦРП 5%
                in_out_all_crp = (
                    diff_in_out
                    * arr_in_out_all_y["category"][0]["total"][month]["percent"]
                    / 100
                )
                arr_in_out_all_y["category"][0]["total"][month][
                    "amount_month"
                ] = in_out_all_crp
                # КВ 20% ЦРП 50%

                in_out_all_crp_kv = (
                    diff_in_out
                    * arr_in_out_all_y["category"][1]["total"][month]["percent"]
                    / 100
                )
                arr_in_out_all_y["category"][1]["total"][month][
                    "amount_month"
                ] = in_out_all_crp_kv
                # всего выводим с ИП (премии+КВ+остатки)
                bonus = arr_in_out_all_y["category"][2]["total"][month]["amount_month"]
                all_out_check = bonus + in_out_all_crp_kv + in_out_all_crp
                arr_in_out_all_y["category"][3]["total"][month][
                    "amount_month"
                ] = all_out_check

                # ПРОВЕРКА ДОХОД-РАСХОД =B12-B23- B27-B28- B38-B40
                total_oper_and_nalog = arr_inside_all_y["total_category"]["total"][
                    month
                ]["amount_month"]
                total_check = (
                    diff_in_out
                    - in_out_all_crp_kv
                    - in_out_all_crp
                    - total_oper_and_nalog
                )
                arr_in_out_after_all_y["category"][0]["total"][month][
                    "amount_month"
                ] = total_check

                # ПРОВЕРКА =B12-B23 -B27-B28-B38-B40 -B29
                total_check_sver = total_check - bonus
                arr_in_out_all_y["category"][4]["total"][month][
                    "amount_month"
                ] = total_check_sver

                # ДОХОД-РАСХОД+отложенные налоги
                nalog = arr_inside_all_y["category"][0]["total"]["total"][month][
                    "amount_month"
                ]

                total_check_sver_and_nalog = total_check + nalog
                arr_in_out_after_all_y["category"][1]["total"][month][
                    "amount_month"
                ] = total_check_sver_and_nalog

                # БЛОК ПРЦЕНЫ СОБСТВЕННИКУ И ВЛАДЕЛЬЦУ
                # на квартальную премию собственникам

                if arr_summ_to_persent_y["category"][0]["total"][month]["chek"] == True:
                    to_kvartal_bonus = arr_summ_to_persent_y["category"][0]["total"][
                        month
                    ]["amount_month_chek"]
                else:
                    to_kvartal_bonus = (
                        in_out_all_crp
                        * arr_summ_to_persent_y["category"][0]["total"][month][
                            "percent"
                        ]
                        / 100
                    )
                arr_summ_to_persent_y["category"][0]["total"][month][
                    "amount_month"
                ] = to_kvartal_bonus

                # компенсация владельцу с ИП
                if arr_summ_to_persent_y["category"][1]["total"][month]["chek"] == True:
                    to_boss = arr_summ_to_persent_y["category"][1]["total"][month][
                        "amount_month_chek"
                    ]
                else:
                    to_boss = (
                        in_out_all_crp_kv
                        * arr_summ_to_persent_y["category"][1]["total"][month][
                            "percent"
                        ]
                        / 100
                    )
                arr_summ_to_persent_y["category"][1]["total"][month][
                    "amount_month"
                ] = to_boss

                # В ХРАНИЛИЩЕ:
                # остаток ПРИБЫЛЬ 1% ЦРП 5%
                after_prs_crp = in_out_all_crp - to_kvartal_bonus
                if arr_keep_y["category"][0]["total"][month]["chek"]:
                    # заполненно из операций
                    pass
                else:
                    arr_keep_y["category"][0]["total"][month][
                        "amount_month"
                    ] = after_prs_crp

                # остаток КВ 0,5 % ЦРП 50%
                after_prs_kv = in_out_all_crp_kv - to_boss
                if arr_keep_y["category"][1]["total"][month]["chek"]:
                    # заполненно из операций
                    pass
                else:
                    arr_keep_y["category"][1]["total"][month][
                        "amount_month"
                    ] = after_prs_kv

                # вывод остатков ООО в Хранилище
                # in_ooo_bonus = arr_in_y["category"][1]["group"][
                #     "ПЕРЕВОД ОСТАТКОВ С ООО"
                # ][month]["amount_month"]

                # if arr_keep_y["category"][2]["total"][month]["chek"]:
                #     # заполненно из операций
                #     pass
                # else:
                #     if arr_keep_y["category"][2]["total"][month]["amount_month"] == 0:
                #         arr_keep_y["category"][2]["total"][month][
                #             "amount_month"
                #         ] = in_ooo_bonus
                #     else:
                #         pass

                # ИТОГО В ХРАНИЛИЩЕ из $:
                total_to_storage = (
                    arr_keep_y["category"][0]["total"][month]["amount_month"]
                    + arr_keep_y["category"][1]["total"][month]["amount_month"]
                    + arr_keep_y["category"][2]["total"][month]["amount_month"]
                )
                arr_keep_y["total_category"]["total"][month][
                    "amount_month"
                ] = total_to_storage

                # остаток на конец месяца

                for i, month in enumerate(months_year):
                    if i + 1 < len(months_year):
                        month_prev = months_year[i + 1]
                        prev_all_sum_month = arr_end_month_y["total"][month_prev][
                            "amount_month"
                        ]

                    else:
                        # Для самого последнего месяца (например, "Январь") — остаток на конец декабря прошлого года, если есть
                        prev_all_sum_month = 0
                        if old_oper_arr:
                            prev_year = year - 1
                            last_month = "Декабрь"
                            prev_year_data = old_oper_arr.get(prev_year)
                            if prev_year_data:
                                try:
                                    category_list = prev_year_data[
                                        "arr_in_out_after_all_total"
                                    ]["category"]
                                    prev_all_sum_month = category_list[3]["total"][
                                        last_month
                                    ]["amount_month"]
                                except Exception as e:
                                    print(
                                        "Ошибка при доступе к остатку прошлого года (old_oper_arr):",
                                        e,
                                    )
                                    prev_all_sum_month = 0

                    nalog_real = arr_in_out_after_all_y["category"][2]["total"][month][
                        "amount_month"
                    ]
                    all_sum_month = (
                        total_check_sver_and_nalog - nalog_real + prev_all_sum_month
                    )

                    arr_end_month_y["total"][month]["amount_month"] = all_sum_month

                # Р/С на начало месяца
                # получить следующий месяц
                for i, month in enumerate(months_year):
                    if i == len(months_year) - 1:
                        # Для самого последнего месяца (например, "Январь") — остаток на конец декабря прошлого года, если есть
                        last_balance = 0
                        if old_oper_arr:
                            prev_year = year - 1
                            last_month = "Декабрь"
                            prev_year_data = old_oper_arr.get(prev_year)
                            if prev_year_data:
                                try:
                                    category_list = prev_year_data[
                                        "arr_in_out_after_all_total"
                                    ]["category"]
                                    last_balance = category_list[3]["total"][
                                        last_month
                                    ]["amount_month"]
                                except Exception as e:
                                    print(
                                        "Ошибка при доступе к остатку прошлого года (old_oper_arr):",
                                        e,
                                    )
                                    last_balance = 0
                        arr_start_month_y["total"][month]["amount_month"] = last_balance
                    else:
                        next_month = months_year[i + 1]
                        arr_start_month_y["total"][month]["amount_month"] = (
                            arr_end_month_y["total"][next_month]["amount_month"]
                        )

            arr_start_month_y = reverse_months_in_dict(arr_start_month_y)
            arr_in_y = reverse_months_in_dict(arr_in_y)
            arr_out_y = reverse_months_in_dict(arr_out_y)
            arr_in_out_all_y = reverse_months_in_dict(arr_in_out_all_y)
            arr_real_diff_y = reverse_months_in_dict(arr_real_diff_y)
            arr_inside_all_y = reverse_months_in_dict(arr_inside_all_y)
            arr_in_out_after_all_y = reverse_months_in_dict(arr_in_out_after_all_y)
            arr_summ_to_persent_y = reverse_months_in_dict(arr_summ_to_persent_y)
            arr_keep_y = reverse_months_in_dict(arr_keep_y)
            arr_end_month_y = reverse_months_in_dict(arr_end_month_y)

            months_year = list(reversed(months_year))

            operations_actual = {
                "arr_start_month": arr_start_month_y,
                "arr_in": arr_in_y,
                "arr_out": arr_out_y,
                "arr_in_out_all": arr_in_out_all_y,
                "arr_real_diff": arr_real_diff_y,
                "arr_inside_all": arr_inside_all_y,
                "arr_in_out_after_all": arr_in_out_after_all_y,
                "arr_summ_to_persent": arr_summ_to_persent_y,
                "arr_keep": arr_keep_y,
                "arr_end_month": arr_end_month_y,
                "months_current_year": months_year,
                "year": year,
            }

            operations_by_year[year] = operations_actual
            operations_by_year = dict(sorted(operations_by_year.items(), reverse=True))
            return operations_by_year

    else:
        # Добавляем категории из CATEGORY_OPERACCOUNT
        for categ_oper in CATEGORY_OPERACCOUNT:

            arr_inside_all["category"][1]["group"][categ_oper[1]] = {}
            # Добавляем месяцы для каждой категории
            for i, month in enumerate(months_current_year):
                month_number = month_numbers[month]
                arr_inside_all["category"][1]["group"][categ_oper[1]][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

        # Добавляем месяцы
        for i, month in enumerate(months_current_year):
            month_number = month_numbers[month]
            # рс на анчало меясца
            arr_start_month["total"][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
            }
            # рс на конец меясца
            arr_end_month_ip["total"][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
            }

            # СУБПОДРЯДЧИКИ + ПЛОЩАДКИ, в т.ч.
            arr_out["total_category"]["total"][month] = {
                "amount_month": 0,
                "month_number": f"{month_number:02d}",
                "is_make_operations": False,
            }
            arr_out["category"][1]["group"]["вывод $ для оплаты субподряда (вручную)"][
                month
            ] = {
                "is_make_operations": True,
                "bank_out": between_id_ip_to_mir["bank_to"],
                "date_start": datetime.datetime(
                    year_now, MONTHS_RU.index(month) + 1, 1
                ),
                "operation_id": 0,
                "type_operations": "between",
                "between_id": between_id_ip_to_mir["id"],
                "amount_month": 0,
                "expected": 0,
            }
            arr_out["category"][1]["group"]["вывод остатков ООО в Хранилище"][month] = {
                "is_make_operations": True,
                "bank_out": between_id_for_ooo_ip_to_storage["bank_to"],
                "date_start": datetime.datetime(
                    year_now, MONTHS_RU.index(month) + 1, 1
                ),
                "operation_id": 0,
                "type_operations": "between",
                "between_id": between_id_for_ooo_ip_to_storage["id"],
                "amount_month": 0,
                "expected": 0,
            }

            # первый блок доход расход
            for in_out in arr_in_out_all["category"]:

                in_out["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                if in_out["name"] == "ПРИБЫЛЬ 1% ЦРП 5%":
                    in_out["total"][month]["is_make_operations"] = True
                    in_out["total"][month]["type_operations"] = "percent"
                    in_out["total"][month]["expected"] = 0

                    in_out["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    in_out["total"][month]["id_groupe"] = categ_percent_crp["id"]

                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_crp["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    in_out["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    in_out["total"][month]["operation_percent_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )

                elif in_out["name"] == "КВ 20% ЦРП 50%":
                    in_out["total"][month]["is_make_operations"] = True
                    in_out["total"][month]["type_operations"] = "percent"
                    in_out["total"][month]["expected"] = 0

                    in_out["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    in_out["total"][month]["id_groupe"] = categ_percent_crp_kv["id"]

                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_crp_kv["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    in_out["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    in_out["total"][month]["operation_percent_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )
            
                elif in_out["name"] == "ПРЕМИИ":
                    in_out["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    in_out["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    in_out["total"][month]["is_make_operations"] = True

                    in_out["total"][month]["bank_out"] = (
                        between_id_for_ip_to_storage_bonus["bank_to"]
                    )
                    in_out["total"][month]["operation_id"] = 0
                    in_out["total"][month]["type_operations"] = "between"
                    in_out["total"][month]["between_id"] = (
                        between_id_for_ip_to_storage_bonus["id"]
                    )
                    in_out["total"][month]["amount_month_chek"] = 0
                    in_out["total"][month]["chek"] = False
            
            # второй  блок доход расход
            for in_out_after in arr_in_out_after_all["category"]:
                in_out_after["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                if in_out_after["name"] == "ФАКТИЧЕСКАЯ ОПЛАТА НАЛОГОВ":
                    in_out_after["total"][month]["is_make_operations"] = True
                    in_out_after["total"][month]["bank_out"] = 5
                    in_out_after["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    in_out_after["total"][month]["operation_id"] = 0
                    in_out_after["total"][month]["type_operations"] = "nalog"
                    in_out_after["total"][month]["id_groupe"] = categoru_nalog_fact[
                        "id"
                    ]

            # В ХРАНИЛИЩЕ:
            arr_keep_ip["total_category"]["total"][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
            }
            for keep_ip in arr_keep_ip["category"]:
                if keep_ip["name"] == "остаток ПРИБЫЛЬ 1% ЦРП 5%":
                    keep_ip["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    keep_ip["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    keep_ip["total"][month]["is_make_operations"] = True

                    keep_ip["total"][month]["bank_out"] = (
                        between_id_for_ooo_ip_to_storage_crp["bank_to"]
                    )
                    keep_ip["total"][month]["operation_id"] = 0
                    keep_ip["total"][month]["type_operations"] = "between"
                    keep_ip["total"][month]["between_id"] = (
                        between_id_for_ooo_ip_to_storage_crp["id"]
                    )
                    keep_ip["total"][month]["amount_month_chek"] = 0
                    keep_ip["total"][month]["chek"] = False
                elif keep_ip["name"] == "остаток КВ 0,5 % ЦРП 50%":
                    keep_ip["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    keep_ip["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    keep_ip["total"][month]["is_make_operations"] = True

                    keep_ip["total"][month]["bank_out"] = (
                        between_id_for_ooo_ip_to_storage_kv["bank_to"]
                    )
                    keep_ip["total"][month]["operation_id"] = 0
                    keep_ip["total"][month]["type_operations"] = "between"
                    keep_ip["total"][month]["between_id"] = (
                        between_id_for_ooo_ip_to_storage_kv["id"]
                    )
                    keep_ip["total"][month]["amount_month_chek"] = 0
                    keep_ip["total"][month]["chek"] = False
                elif keep_ip["name"] == "вывод остатков ООО в Хранилище":
                    keep_ip["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    keep_ip["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    keep_ip["total"][month]["is_make_operations"] = True

                    keep_ip["total"][month]["bank_out"] = (
                        between_id_for_ooo_ip_to_storage_kv["bank_to"]
                    )
                    keep_ip["total"][month]["operation_id"] = 0
                    keep_ip["total"][month]["type_operations"] = "between"
                    keep_ip["total"][month]["between_id"] = (
                        between_id_for_ooo_ip_to_storage_kv["id"]
                    )
                    keep_ip["total"][month]["amount_month_chek"] = 0
                    keep_ip["total"][month]["chek"] = False

            for summ_to_persent in arr_summ_to_persent["category"]:
                summ_to_persent["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                if summ_to_persent["name"] == "на квартальную премию собственникам":
                    summ_to_persent["total"][month]["is_make_operations"] = True
                    summ_to_persent["total"][month]["type_operations"] = "percent"

                    summ_to_persent["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    summ_to_persent["total"][month]["id_groupe"] = (
                        categ_percent_to_boss["id"]
                    )
                    summ_to_persent["total"][month]["between_id"] = (
                        categ_percent_to_boss["category_between"]
                    )
                    summ_to_persent["total"][month]["bank_out"] = categ_percent_to_boss[
                        "category_between__bank_to"
                    ]
                    summ_to_persent["total"][month]["amount_month_chek"] = 0
                    summ_to_persent["total"][month]["chek"] = False

                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_to_boss["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    summ_to_persent["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    summ_to_persent["total"][month]["operation_percent_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )

                elif summ_to_persent["name"] == "компенсация владельцу с ИП":
                    summ_to_persent["total"][month]["is_make_operations"] = True
                    summ_to_persent["total"][month]["type_operations"] = "percent"

                    summ_to_persent["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    summ_to_persent["total"][month]["id_groupe"] = (
                        categ_percent_to_boss2["id"]
                    )
                    summ_to_persent["total"][month]["between_id"] = (
                        categ_percent_to_boss2["category_between"]
                    )
                    summ_to_persent["total"][month]["bank_out"] = (
                        categ_percent_to_boss2["category_between__bank_to"]
                    )
                    summ_to_persent["total"][month]["amount_month_chek"] = 0
                    summ_to_persent["total"][month]["chek"] = False

                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_to_boss2["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    summ_to_persent["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    summ_to_persent["total"][month]["operation_percent_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )

            # внутренние счета расходы все
            arr_inside_all["total_category"]["total"][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
            }

            for inside_all in arr_inside_all["category"]:
                inside_all["total"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                if inside_all["name"] == "НАЛОГИ ИП (откладываем до оплаты):":
                    inside_all["group"]["ИТОГО налоги на ИП"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }

        for service in services:
            name = f"{service.name}({service.name_long_ru})"
            arr_in["category"][0]["group"][name] = {}

            for i, month in enumerate(months_current_year):
                month_number = month_numbers[month]

                # Для услуг
                arr_in["category"][0]["group"][name][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

                # Для переводов с ооо
                arr_in["category"][1]["group"]["на премии"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }
                arr_in["category"][1]["group"]["ООО прибыль ЦРП 5%"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }
                # Для переводов с ооо
                arr_in["category"][1]["group"]["перевод с ООО для оплаты субподряда"][
                    month
                ] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }
                arr_in["category"][1]["group"]["зачисление $ для оплаты субподряда"][
                    month
                ] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }
                arr_in["category"][1]["group"]["зачисление из хранилища"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }
                # Для переводов с ооо
                arr_in["category"][1]["group"]["ПЕРЕВОД ОСТАТКОВ С ООО"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

                # Для итогов
                arr_in["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

                # Для arr_out
                # Добавляем месяцы для других субподрядов
                for category in other_categ_subkontract:

                    if category.name not in arr_out["category"][2]["group"]:
                        arr_out["category"][2]["group"][category.name] = {}
                        # Инициализируем месяцы для каждой категории
                        for i, month in enumerate(months_current_year):
                            month_number = month_numbers[month]
                            arr_out["category"][2]["group"][category.name][month] = {
                                "amount_month": 0,
                                "month_number": MONTHS_RU.index(month) + 1,
                                "is_make_operations": True,
                                "bank_out": 5,
                                "date_start": datetime.datetime(
                                    year_now, MONTHS_RU.index(month) + 1, 1
                                ),
                                "operation_id": 0,
                                "type_operations": "SubcontractOtherCategory",
                                "id_groupe": category.id,
                                "expected": 0,
                            }

                arr_out["category"][0]["group"][name] = {}
                for i, month in enumerate(months_current_year):
                    arr_out["category"][0]["group"][name][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

                # Добавляем месяцы для итогов arr_out
                arr_out["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

        # распределение операций
        for operation in operations:
            month_name = MONTHS_RU[operation.data.month - 1]
            prev_month = (
                MONTHS_RU[operation.data.month] if operation.data.month < 12 else None
            )
            is_prev_month = prev_month in months_current_year if prev_month else False

            # операции ВНУТРЕННИЕ СЧЕТА
            if operation.operaccount:
                id_operacc_categ = get_id_categ_oper(operation.operaccount.category)
                arr_inside_all["category"][1]["group"][id_operacc_categ][month_name][
                    "amount_month"
                ] += operation.amount
                arr_inside_all["category"][1]["total"]["total"][month_name][
                    "amount_month"
                ] += operation.amount

                arr_inside_all["total_category"]["total"][month_name][
                    "amount_month"
                ] += operation.amount
            # операции налоги
            elif operation.nalog:
                if operation.nalog.id != 10:
                    arr_inside_all["category"][0]["total"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                    arr_inside_all["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                else:
                    arr_in_out_after_all["category"][2]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                    arr_in_out_after_all["category"][2]["total"][month_name][
                        "operation_id"
                    ] = operation.id
            # операции прихода по договорам услуг
            elif operation.monthly_bill and operation.suborder is None:
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

            elif operation.suborder_other:
                # # Добавляем в общий итог по месяцу операции
                arr_out["total_category"]["total"][month_name][
                    "amount_month"
                ] += operation.amount

                service_name = operation.suborder_other.name
                arr_out["category"][2]["group"][service_name][month_name][
                    "amount_month"
                ] += operation.amount
                arr_out["category"][2]["group"][service_name][month_name][
                    "operation_id"
                ] = operation.id
                if is_prev_month:
                    arr_out["category"][2]["group"][service_name][prev_month][
                        "expected"
                    ] += operation.amount

            elif operation.between_bank:
                # исходящее между счетами
                if operation.bank_in == bank:
                    if (
                        operation.between_bank.name
                        == "вывод $ для оплаты субподряда (вручную)"
                    ):
                        arr_out["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_out["category"][1]["group"][
                            "вывод $ для оплаты субподряда (вручную)"
                        ][month_name]["amount_month"] += operation.amount
                        arr_out["category"][1]["group"][
                            "вывод $ для оплаты субподряда (вручную)"
                        ][month_name]["operation_id"] = operation.id

                        if is_prev_month:
                            arr_out["category"][1]["group"][
                                "вывод $ для оплаты субподряда (вручную)"
                            ][prev_month]["expected"] += operation.amount
                    elif (
                        operation.between_bank.name == "вывод остатков ООО в Хранилище"
                    ):
                        arr_out["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_out["category"][1]["group"][
                            "вывод остатков ООО в Хранилище"
                        ][month_name]["amount_month"] += operation.amount
                        arr_out["category"][1]["group"][
                            "вывод остатков ООО в Хранилище"
                        ][month_name]["operation_id"] = operation.id

                        arr_keep_ip["category"][2]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_keep_ip["category"][2]["total"][month_name][
                            "operation_id"
                        ] = operation.id
                        arr_keep_ip["category"][2]["total"][month_name]["chek"] = True

                    elif operation.between_bank.name == "остаток ПРИБЫЛЬ 1% ЦРП 5%":
                        pass
                        arr_keep_ip["category"][0]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_keep_ip["category"][0]["total"][month_name][
                            "operation_id"
                        ] = operation.id
                        arr_keep_ip["category"][0]["total"][month_name]["chek"] = True

                    elif operation.between_bank.name == "остаток КВ 0,5 % ЦРП 50%":
                        pass
                        arr_keep_ip["category"][1]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_keep_ip["category"][1]["total"][month_name][
                            "operation_id"
                        ] = operation.id
                        arr_keep_ip["category"][1]["total"][month_name]["chek"] = True

                    elif (
                        operation.between_bank.name
                        == "на квартальную премию собственникам"
                    ):

                        name_to_find = "на квартальную премию собственникам"
                        item = next(
                            (
                                x
                                for x in arr_summ_to_persent["category"]
                                if x["name"] == name_to_find
                            ),
                            None,
                        )
                        if item:
                            item["total"][month_name][
                                "amount_month_chek"
                            ] += operation.amount
                            item["total"][month_name]["operation_id"] = operation.id
                            item["total"][month_name]["chek"] = True

                    elif operation.between_bank.name == "компенсация владельцу с ИП":

                        name_to_find = "компенсация владельцу с ИП"
                        item = next(
                            (
                                x
                                for x in arr_summ_to_persent["category"]
                                if x["name"] == name_to_find
                            ),
                            None,
                        )
                        if item:
                            item["total"][month_name][
                                "amount_month_chek"
                            ] += operation.amount
                            item["total"][month_name]["operation_id"] = operation.id
                            item["total"][month_name]["chek"] = True
                    
                    elif operation.between_bank.name == "ПРЕМИИ":
                        arr_in_out_all["category"][2]["total"][month_name][
                            "amount_month"
                        ] = operation.amount
                        arr_in_out_all["category"][2]["total"][month_name][
                            "operation_id"
                        ] = operation.id
                        arr_in_out_all["category"][2]["total"][month_name]["chek"] = True
                        
                # приходящее между счетами
                if operation.bank_to == bank:
                    if (
                        operation.between_bank.name
                        == "перевод на ИП для оплаты субподряда"
                    ):
                        arr_in["category"][1]["group"][
                            "перевод с ООО для оплаты субподряда"
                        ][month_name]["amount_month"] += operation.amount
                        arr_in["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                    elif (
                        operation.between_bank.name
                        == "зачисление на ИП для оплаты субподряда"
                    ):
                        arr_in["category"][1]["group"][
                            "зачисление $ для оплаты субподряда"
                        ][month_name]["amount_month"] += operation.amount
                        arr_in["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                    elif operation.between_bank.name == "зачисление на ИП":
                        arr_in["category"][1]["group"]["зачисление из хранилища"][
                            month_name
                        ]["amount_month"] += operation.amount
                        arr_in["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

                    elif operation.between_bank.name == "ПРЕМИИ":
                        arr_in["category"][1]["group"]["на премии"][month_name][
                            "amount_month"
                        ] = operation.amount
                        arr_in["total_category"]["total"][month_name][
                            "amount_month"
                        ] = operation.amount

                        if arr_in_out_all["category"][2]["total"][month_name][
                            "amount_month"
                        ] == 0:
                            arr_in_out_all["category"][2]["total"][month_name][
                                "amount_month"
                            ] = operation.amount
                        
                        
                        

                    elif (
                        operation.between_bank.name
                        == "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП"
                    ):
                        arr_in["category"][1]["group"]["ПЕРЕВОД ОСТАТКОВ С ООО"][
                            month_name
                        ]["amount_month"] += operation.amount
                        arr_in["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        # if arr_keep_ip["category"][2]["total"][
                        #     month_name
                        # ]["amount_month"] :
                        #     arr_keep_ip["category"][2]["total"][
                        #         month_name
                        #     ]["amount_month"] += operation.amount
                        
                        # arr_keep_ip["category"][2]["total"][
                        #     month_name
                        # ]["amount_month"] += operation.amount
                        # arr_keep_ip["total_category"]["total"][month_name][
                        #     "amount_month"
                        # ] += operation.amount

            # данные из кеша других страниц

        # данные из кеша других страниц
        if context_ooo and isinstance(context_ooo, dict):
            for key, value in context_ooo.items():

                # --- Обработка arr_in_out_all из кеша ---
                if key == "arr_in_out_all":
                    arr_in_out_all_ooo = value
                    for category in arr_in_out_all_ooo.get("category", []):
                        if category.get("name") == "ПРИБЫЛЬ 1% ЦРП 5%":
                            total = category.get("total", {})
                            for month_name, month_data in total.items():
                                if month_data.get("chek") is True:
                                    v = month_data.get("amount_month_chek", 0)

                                else:
                                    v = month_data.get("amount_month", 0)

                                # Безопасная инициализация и прибавление
                                group = arr_in["category"][1]["group"]
                                group.setdefault("ООО прибыль ЦРП 5%", {})
                                group["ООО прибыль ЦРП 5%"].setdefault(month_name, {})
                                group["ООО прибыль ЦРП 5%"][month_name].setdefault(
                                    "amount_month", 0
                                )
                                group["ООО прибыль ЦРП 5%"][month_name][
                                    "amount_month"
                                ] += v

                                # Аналогично для total_category
                                total_cat = arr_in["total_category"]["total"]
                                total_cat.setdefault(month_name, {})
                                total_cat[month_name].setdefault("amount_month", 0)
                                total_cat[month_name]["amount_month"] += v
                        elif category.get("name") == "КВ 20% ЦРП 50%":
                            total = category.get("total", {})
                            for month_name, month_data in total.items():
                                if month_data.get("chek") is True:
                                    v = month_data.get("amount_month_chek", 0)

                                else:
                                    v = month_data.get("amount_month", 0)

                                # Безопасная инициализация и прибавление
                                group = arr_in["category"][1]["group"]
                                group.setdefault("ООО КВ ЦРП 50%", {})
                                group["ООО КВ ЦРП 50%"].setdefault(month_name, {})
                                group["ООО КВ ЦРП 50%"][month_name].setdefault(
                                    "amount_month", 0
                                )
                                group["ООО КВ ЦРП 50%"][month_name]["amount_month"] += v

                                # Аналогично для total_category
                                total_cat = arr_in["total_category"]["total"]
                                total_cat.setdefault(month_name, {})
                                total_cat[month_name].setdefault("amount_month", 0)
                                total_cat[month_name]["amount_month"] += v

        # разные общие суммы
        for i, month in enumerate(months_current_year):
            # === РЕАЛЬНЫЕ ПОСТУПЛЕНИЯ ИП (ВЫРУЧКА-СУБПОДРЯД)" ===
            in_sum = (
                arr_in["total_category"]["total"].get(month, {}).get("amount_month", 0)
            )
            out_sum = (
                arr_out["total_category"]["total"].get(month, {}).get("amount_month", 0)
            )
            if month not in arr_real_diff["total"]:
                arr_real_diff["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
            diff_in_out = in_sum - out_sum
            arr_real_diff["total"][month]["amount_month"] = diff_in_out
            # # ПРИБЫЛЬ 1% ЦРП 5%

            in_out_all_crp = (
                diff_in_out
                * arr_in_out_all["category"][0]["total"][month]["percent"]
                / 100
            )
            arr_in_out_all["category"][0]["total"][month][
                "amount_month"
            ] = in_out_all_crp
            # КВ 20% ЦРП 50%

            in_out_all_crp_kv = (
                diff_in_out
                * arr_in_out_all["category"][1]["total"][month]["percent"]
                / 100
            )
            arr_in_out_all["category"][1]["total"][month][
                "amount_month"
            ] = in_out_all_crp_kv
            # всего выводим с ИП (премии+КВ+остатки)
            bonus = arr_in_out_all["category"][2]["total"][month]["amount_month"]
            all_out_check = bonus + in_out_all_crp_kv + in_out_all_crp
            arr_in_out_all["category"][3]["total"][month][
                "amount_month"
            ] = all_out_check

            # ПРОВЕРКА ДОХОД-РАСХОД =B12-B23- B27-B28- B38-B40
            total_oper_and_nalog = arr_inside_all["total_category"]["total"][month][
                "amount_month"
            ]
            total_check = (
                diff_in_out - in_out_all_crp_kv - in_out_all_crp - total_oper_and_nalog
            )
            arr_in_out_after_all["category"][0]["total"][month][
                "amount_month"
            ] = total_check

            # ПРОВЕРКА =B12-B23 -B27-B28-B38-B40 -B29
            total_check_sver = total_check - bonus
            arr_in_out_all["category"][4]["total"][month][
                "amount_month"
            ] = total_check_sver

            # ДОХОД-РАСХОД+отложенные налоги
            nalog = arr_inside_all["category"][0]["total"]["total"][month][
                "amount_month"
            ]

            total_check_sver_and_nalog = total_check + nalog
            arr_in_out_after_all["category"][1]["total"][month][
                "amount_month"
            ] = total_check_sver_and_nalog

            # БЛОК ПРЦЕНЫ СОБСТВЕННИКУ И ВЛАДЕЛЬЦУ
            # на квартальную премию собственникам

            if arr_summ_to_persent["category"][0]["total"][month]["chek"] == True:
                to_kvartal_bonus = arr_summ_to_persent["category"][0]["total"][month][
                    "amount_month_chek"
                ]
            else:
                to_kvartal_bonus = (
                    in_out_all_crp
                    * arr_summ_to_persent["category"][0]["total"][month]["percent"]
                    / 100
                )
            arr_summ_to_persent["category"][0]["total"][month][
                "amount_month"
            ] = to_kvartal_bonus

            # компенсация владельцу с ИП
            if arr_summ_to_persent["category"][1]["total"][month]["chek"] == True:
                to_boss = arr_summ_to_persent["category"][1]["total"][month][
                    "amount_month_chek"
                ]
            else:
                to_boss = (
                    in_out_all_crp_kv
                    * arr_summ_to_persent["category"][1]["total"][month]["percent"]
                    / 100
                )
            arr_summ_to_persent["category"][1]["total"][month]["amount_month"] = to_boss

            # В ХРАНИЛИЩЕ:
            # остаток ПРИБЫЛЬ 1% ЦРП 5%
            after_prs_crp = in_out_all_crp - to_kvartal_bonus
            if arr_keep_ip["category"][0]["total"][month]["chek"]:
                # заполненно из операций
                pass
            else:
                arr_keep_ip["category"][0]["total"][month][
                    "amount_month"
                ] = after_prs_crp

            # остаток КВ 0,5 % ЦРП 50%
            after_prs_kv = in_out_all_crp_kv - to_boss
            if arr_keep_ip["category"][1]["total"][month]["chek"]:
                # заполненно из операций
                pass
            else:
                arr_keep_ip["category"][1]["total"][month][
                    "amount_month"
                ] = after_prs_kv

            # вывод остатков ООО в Хранилище
            # in_ooo_bonus = arr_in["category"][1]["group"]["ПЕРЕВОД ОСТАТКОВ С ООО"][
            #     month
            # ]["amount_month"]

            # if arr_keep_ip["category"][2]["total"][month]["chek"]:
            #     # заполненно из операций
            #     pass
            # else:
            #     if arr_keep_ip["category"][2]["total"][month]["amount_month"] == 0:
            #         arr_keep_ip["category"][2]["total"][month][
            #             "amount_month"
            #         ] = in_ooo_bonus
            #     else:
            #         pass

            # ИТОГО В ХРАНИЛИЩЕ из $:
            total_to_storage = (
                arr_keep_ip["category"][0]["total"][month]["amount_month"]
                + arr_keep_ip["category"][1]["total"][month]["amount_month"]
                + arr_keep_ip["category"][2]["total"][month]["amount_month"]
            )
            arr_keep_ip["total_category"]["total"][month][
                "amount_month"
            ] = total_to_storage

            # остаток на конец месяца

            for i, month in enumerate(months_current_year):
                if i + 1 < len(months_current_year):
                    month_prev = months_current_year[i + 1]
                    prev_all_sum_month = arr_end_month_ip["total"][month_prev][
                        "amount_month"
                    ]
                    arr_in_out_all["category"][0]["total"][month]["expected"] = arr_in_out_all["category"][0]["total"][month_prev]["percent"]
                    arr_in_out_all["category"][1]["total"][month]["expected"] = arr_in_out_all["category"][1]["total"][month_prev]["percent"]
                    arr_summ_to_persent["category"][0]["total"][month]["expected"] = arr_summ_to_persent["category"][0]["total"][month_prev]["percent"]
                    arr_summ_to_persent["category"][1]["total"][month]["expected"] = arr_summ_to_persent["category"][1]["total"][month_prev]["percent"] 
                else:
                    # Для самого последнего месяца (например, "Январь") — остаток на конец декабря прошлого года, если есть
                    prev_all_sum_month = 0
                    if old_oper_arr:
                        prev_year = year_now - 1

                        last_month = "Декабрь"
                        prev_year_data = old_oper_arr.get(prev_year)
                        if prev_year_data:
                            try:
                                arr_end_month_ip["total"][month]["amount_month"]
                                category_list = prev_year_data["arr_end_month_ip"][
                                    "category"
                                ]
                                prev_all_sum_month = prev_year_data["arr_end_month_ip"][
                                    "total"
                                ][last_month]["amount_month"]

                            except Exception as e:
                                print(
                                    "Ошибка при доступе к остатку прошлого года (old_oper_arr):",
                                    e,
                                )
                                prev_all_sum_month = 0

                nalog_real = arr_in_out_after_all["category"][2]["total"][month][
                    "amount_month"
                ]
                all_sum_month = (
                    total_check_sver_and_nalog - nalog_real + prev_all_sum_month
                )

                arr_end_month_ip["total"][month]["amount_month"] = all_sum_month

            # Р/С на начало месяца
            # получить следующий месяц
            for i, month in enumerate(months_current_year):
                if i == len(months_current_year) - 1:
                    # Для самого последнего месяца (например, "Январь") — остаток на конец декабря прошлого года, если есть
                    last_balance = 0
                    if old_oper_arr:
                        prev_year = year_now - 1
                        last_month = "Декабрь"
                        prev_year_data = old_oper_arr.get(prev_year)

                        if prev_year_data:
                            try:
                                category_list = prev_year_data[
                                    "arr_in_out_after_all_total"
                                ]["category"]
                                last_balance = category_list[3]["total"][last_month][
                                    "amount_month"
                                ]
                            except Exception as e:
                                print(
                                    "Ошибка при доступе к остатку прошлого года (old_oper_arr):",
                                    e,
                                )
                                last_balance = 0
                    arr_start_month["total"][month]["amount_month"] = last_balance
                else:
                    next_month = months_current_year[i + 1]
                    arr_start_month["total"][month]["amount_month"] = arr_end_month_ip[
                        "total"
                    ][next_month]["amount_month"]
                    # (
                    #     arr_in_out_after_all_total["category"][3]["total"][next_month][
                    #         "amount_month"
                    #     ]
                    # )

        return (
            arr_start_month,
            arr_in,
            arr_out,
            arr_in_out_all,
            arr_real_diff,
            arr_inside_all,
            arr_in_out_after_all,
            arr_summ_to_persent,
            arr_keep_ip,
            arr_end_month_ip,
        )


def fill_operations_arrays_nal(
    categ_percent_by_name,
    categ_percent_list,
    services,
    arr_in,
    arr_out,
    arr_in_out_all,
    arr_real_diff,
    arr_inside_all,
    arr_summ_to_persent,
    arr_keep,
    CATEGORY_OPERACCOUNT,
    months_current_year,
    month_numbers,
    year_now,
    operations,
    bank,
    cate_oper_beetwen_by_name,
    is_old_oper,
    old_oper_arr,
):

    between_id_nal_to_ip = cate_oper_beetwen_by_name.get(
        "зачисление на ИП для оплаты субподряда"
    )
    between_id_nal_to_storage = cate_oper_beetwen_by_name.get(
        "откладываем в хранилище на будущие расходы"
    )
    between_id_nal_to_storage_crp = cate_oper_beetwen_by_name.get(
        "остаток ПРИБЫЛЬ 1% ЦРП 5%"
    )
    between_id_nal_to_storage_kp = cate_oper_beetwen_by_name.get(
        "остаток КВ 0,5 % ЦРП 50%"
    )
    between_id_nal_to_storage_last = cate_oper_beetwen_by_name.get("остаток $")
    categ_percent_to_boss = categ_percent_by_name.get("на квартальную премию")
    categ_percent_to_boss2 = categ_percent_by_name.get("КВ с $")

    between_id_for_nat_to_storage_bonus = cate_oper_beetwen_by_name.get("ПРЕМИИ")
    categ_percent_crp = categ_percent_by_name.get("ПРИБЫЛЬ 1% ЦРП 5%")
    categ_percent_crp_kv = categ_percent_by_name.get("КВ 0,5 % ЦРП 50%")

    if is_old_oper:

        def reverse_months_in_dict(d):
            if isinstance(d, dict):
                months = [m for m in MONTHS_RU if m in d]
                if len(months) == 12 and set(months) == set(MONTHS_RU):
                    # Это словарь месяцев, разворачиваем в прямой порядок (январь → декабрь)
                    items = [(m, d[m]) for m in MONTHS_RU if m in d]
                    return {k: reverse_months_in_dict(v) for k, v in items}
                else:
                    return {k: reverse_months_in_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [reverse_months_in_dict(x) for x in d]
            else:
                return d

        # Группировка операций по годам
        operations_by_year = {}
        # Получаем уникальные года из операций
        years = set()
        for operation in operations:

            years.add(operation.data.year)

        for year in sorted(years):
            # Фильтруем операции за этот год
            operations_year = [op for op in operations if op.data.year == year]
            # Копируем структуры для этого года
            arr_in_y = copy.deepcopy(arr_in)
            arr_out_y = copy.deepcopy(arr_out)
            arr_in_out_all_y = copy.deepcopy(arr_in_out_all)
            arr_real_diff_y = copy.deepcopy(arr_real_diff)
            arr_inside_all_y = copy.deepcopy(arr_inside_all)
            arr_summ_to_persent_y = copy.deepcopy(arr_summ_to_persent)
            arr_keep_y = copy.deepcopy(arr_keep)

            # months_current_year для этого года
            months_year = [MONTHS_RU[month - 1] for month in range(1, 13)]
            months_year.reverse()
            month_numbers_year = {month: i + 1 for i, month in enumerate(months_year)}

            # --- ОСНОВНОЙ КОД ОБРАБОТКИ ДЛЯ КАЖДОГО ГОДА ---
            # Добавляем категории из CATEGORY_OPERACCOUNT
            for categ_oper in CATEGORY_OPERACCOUNT:

                arr_inside_all_y["category"][1]["group"][categ_oper[1]] = {}
                # Добавляем месяцы для каждой категории
                for i, month in enumerate(months_year):
                    month_number = month_numbers_year[month]
                    arr_inside_all_y["category"][1]["group"][categ_oper[1]][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

            # Добавляем месяцы
            for i, month in enumerate(months_year):
                month_number = month_numbers_year[month]
                arr_real_diff_y["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                for inside_all in arr_inside_all_y["category"]:
                    inside_all["total"]["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                # Для итогов поступления
                # внутренние счета расходы все
                arr_inside_all_y["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }

                arr_in_y["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }
                arr_out_y["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": f"{month_number:02d}",
                    "is_make_operations": False,
                }
                arr_out_y["category"][1]["group"][
                    "зачисление на ИП для оплаты субподряда"
                ][month] = {
                    "is_make_operations": True,
                    "bank_out": between_id_nal_to_ip["bank_to"],
                    "date_start": datetime.datetime(
                        year, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "type_operations": "between",
                    "between_id": between_id_nal_to_ip["id"],
                    "amount_month": 0,
                    "expected": 0,
                }
                arr_out_y["category"][1]["group"][
                    "откладываем в хранилище на будущие расходы"
                ][month] = {
                    "is_make_operations": True,
                    "bank_out": between_id_nal_to_storage["bank_to"],
                    "date_start": datetime.datetime(
                        year, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "type_operations": "between",
                    "between_id": between_id_nal_to_storage["id"],
                    "amount_month": 0,
                    "expected": 0,
                }

                # первый блок доход расход
                for in_out in arr_in_out_all_y["category"]:
                    in_out["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    if in_out["name"] == "ПРИБЫЛЬ 1% ЦРП 5%":
                        in_out["total"][month]["is_make_operations"] = True
                        in_out["total"][month]["type_operations"] = "percent"

                        in_out["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        in_out["total"][month]["id_groupe"] = categ_percent_crp["id"]

                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_crp["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        in_out["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        in_out["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )
                    elif in_out["name"] == "КВ 0,5 % ЦРП 50%":
                        in_out["total"][month]["is_make_operations"] = True
                        in_out["total"][month]["type_operations"] = "percent"

                        in_out["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        in_out["total"][month]["id_groupe"] = categ_percent_crp_kv["id"]

                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_crp_kv["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        in_out["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        in_out["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )
                    elif in_out["name"] == "ПРЕМИИ":
                        in_out["total"][month]["is_make_operations"] = True
                        in_out["total"][month]["bank_out"] = (
                            between_id_for_nat_to_storage_bonus["bank_to"]
                        )
                        in_out["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        in_out["total"][month]["operation_id"] = 0
                        in_out["total"][month]["type_operations"] = "between"
                        in_out["total"][month]["between_id"] = (
                            between_id_for_nat_to_storage_bonus["id"]
                        )

                # В ХРАНИЛИЩЕ:
                arr_keep_y["total_category"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                for keep_ip in arr_keep_y["category"]:
                    if keep_ip["name"] == "остаток ПРИБЫЛЬ 1% ЦРП 5%":
                        keep_ip["total"][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                        }
                        keep_ip["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        keep_ip["total"][month]["is_make_operations"] = True

                        keep_ip["total"][month]["bank_out"] = (
                            between_id_nal_to_storage_crp["bank_to"]
                        )
                        keep_ip["total"][month]["operation_id"] = 0
                        keep_ip["total"][month]["type_operations"] = "between"
                        keep_ip["total"][month]["between_id"] = (
                            between_id_nal_to_storage_crp["id"]
                        )
                        keep_ip["total"][month]["amount_month_chek"] = 0
                        keep_ip["total"][month]["chek"] = False
                    elif keep_ip["name"] == "остаток КВ 0,5 % ЦРП 50%":
                        keep_ip["total"][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                        }
                        keep_ip["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        keep_ip["total"][month]["is_make_operations"] = True

                        keep_ip["total"][month]["bank_out"] = (
                            between_id_nal_to_storage_kp["bank_to"]
                        )
                        keep_ip["total"][month]["operation_id"] = 0
                        keep_ip["total"][month]["type_operations"] = "between"
                        keep_ip["total"][month]["between_id"] = (
                            between_id_nal_to_storage_kp["id"]
                        )
                        keep_ip["total"][month]["amount_month_chek"] = 0
                        keep_ip["total"][month]["chek"] = False
                    elif keep_ip["name"] == "остаток $":
                        keep_ip["total"][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                        }
                        keep_ip["total"][month]["date_start"] = datetime.datetime(
                            year, MONTHS_RU.index(month) + 1, 1
                        )
                        keep_ip["total"][month]["is_make_operations"] = True

                        keep_ip["total"][month]["bank_out"] = (
                            between_id_nal_to_storage_last["bank_to"]
                        )
                        keep_ip["total"][month]["operation_id"] = 0
                        keep_ip["total"][month]["type_operations"] = "between"
                        keep_ip["total"][month]["between_id"] = (
                            between_id_nal_to_storage_last["id"]
                        )
                        keep_ip["total"][month]["amount_month_chek"] = 0
                        keep_ip["total"][month]["chek"] = False
                    elif keep_ip["name"] == "отложенные в хранилище на будущие расходы":
                        keep_ip["total"][month] = {
                            "amount_month": 0,
                            "month_number": MONTHS_RU.index(month) + 1,
                        }

                for summ_to_persent in arr_summ_to_persent_y["category"]:
                    summ_to_persent["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    if summ_to_persent["name"] == "на квартальную премию":
                        summ_to_persent["total"][month]["is_make_operations"] = True
                        summ_to_persent["total"][month]["type_operations"] = "percent"

                        summ_to_persent["total"][month]["date_start"] = (
                            datetime.datetime(year, MONTHS_RU.index(month) + 1, 1)
                        )
                        summ_to_persent["total"][month]["id_groupe"] = (
                            categ_percent_to_boss["id"]
                        )
                        summ_to_persent["total"][month]["between_id"] = (
                            categ_percent_to_boss["category_between"]
                        )
                        summ_to_persent["total"][month]["bank_out"] = (
                            categ_percent_to_boss["category_between__bank_to"]
                        )
                        summ_to_persent["total"][month]["amount_month_chek"] = 0
                        summ_to_persent["total"][month]["chek"] = False

                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_to_boss["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        summ_to_persent["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        summ_to_persent["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )

                    elif summ_to_persent["name"] == "КВ с $":
                        summ_to_persent["total"][month]["is_make_operations"] = True
                        summ_to_persent["total"][month]["type_operations"] = "percent"

                        summ_to_persent["total"][month]["date_start"] = (
                            datetime.datetime(year, MONTHS_RU.index(month) + 1, 1)
                        )
                        summ_to_persent["total"][month]["id_groupe"] = (
                            categ_percent_to_boss2["id"]
                        )
                        summ_to_persent["total"][month]["between_id"] = (
                            categ_percent_to_boss2["category_between"]
                        )
                        summ_to_persent["total"][month]["bank_out"] = (
                            categ_percent_to_boss2["category_between__bank_to"]
                        )
                        summ_to_persent["total"][month]["amount_month_chek"] = 0
                        summ_to_persent["total"][month]["chek"] = False

                        percent_obj = next(
                            (
                                item
                                for item in categ_percent_list
                                if item["category_id"] == categ_percent_to_boss2["id"]
                                and item["data"].month == MONTHS_RU.index(month) + 1
                                and item["data"].year == year
                            ),
                            None,
                        )
                        summ_to_persent["total"][month]["percent"] = (
                            percent_obj["percent"] if percent_obj else 0
                        )
                        summ_to_persent["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )

            # Добавляем месяцы по сервисам
            for service in services:
                name = f"{service.name}({service.name_long_ru})"
                arr_in_y["category"][0]["group"][name] = {}
                arr_out_y["category"][0]["group"][name] = {}
                for i, month in enumerate(months_year):

                    # Для услуг
                    month_number = month_numbers_year[month]
                    arr_in_y["category"][0]["group"][name][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

                    arr_out_y["category"][0]["group"][name][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

            # распределение операций
            for operation in operations_year:
                month_name = MONTHS_RU[operation.data.month - 1]
                prev_month = MONTHS_RU[operation.data.month]
                if operation.monthly_bill and operation.suborder is None:
                    # поступления по договорам услуг

                    service_name = f"{operation.monthly_bill.service.name}({operation.monthly_bill.service.name_long_ru})"

                    if service_name in arr_in_y["category"][0]["group"]:
                        arr_in_y["category"][0]["group"][service_name][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_in["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

                # операции расхода по договорам услуг
                elif operation.suborder:
                    service_name = f"{operation.suborder.month_bill.service.name}({operation.suborder.month_bill.service.name_long_ru})"
                    if service_name in arr_out_y["category"][0]["group"]:
                        arr_out_y["category"][0]["group"][service_name][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_out_y["category"][0]["group"][service_name][month_name][
                            "operation_id"
                        ] = operation.id
                    # Добавляем в общий итог по месяцу операции
                    arr_out_y["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                elif operation.between_bank:
                    if operation.bank_in == bank:
                        if (
                            operation.between_bank.name
                            == "зачисление на ИП для оплаты субподряда"
                        ):
                            arr_out_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "зачисление на ИП для оплаты субподряда"
                            ][month_name]["amount_month"] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "зачисление на ИП для оплаты субподряда"
                            ][month_name]["operation_id"] = operation.id
                        elif (
                            operation.between_bank.name
                            == "откладываем в хранилище на будущие расходы"
                        ):
                            arr_out_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "откладываем в хранилище на будущие расходы"
                            ][month_name]["amount_month"] += operation.amount
                            arr_out_y["category"][1]["group"][
                                "откладываем в хранилище на будущие расходы"
                            ][month_name]["operation_id"] = operation.id

                            arr_keep_y["category"][3]["total"][month_name][
                                "amount_month"
                            ] += operation.amount

                        elif operation.between_bank.name == "ПРЕМИИ":

                            name_to_find = "ПРЕМИИ"
                            item = next(
                                (
                                    x
                                    for x in arr_in_out_all_y["category"]
                                    if x["name"] == name_to_find
                                ),
                                None,
                            )
                            if item:
                                item["total"][month_name][
                                    "amount_month"
                                ] += operation.amount
                                item["total"][month_name]["operation_id"] = operation.id
                        elif operation.between_bank.name == "остаток $":
                            pass
                            arr_keep_y["category"][0]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_keep_y["category"][0]["total"][month_name][
                                "operation_id"
                            ] = operation.id
                            arr_keep_y["category"][0]["total"][month_name][
                                "chek"
                            ] = True
                        elif operation.between_bank.name == "остаток ПРИБЫЛЬ 1% ЦРП 5%":
                            pass
                            arr_keep_y["category"][1]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_keep_y["category"][1]["total"][month_name][
                                "operation_id"
                            ] = operation.id
                            arr_keep_y["category"][1]["total"][month_name][
                                "chek"
                            ] = True

                        elif operation.between_bank.name == "остаток КВ 0,5 % ЦРП 50%":
                            pass
                            arr_keep_y["category"][2]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_keep_y["category"][2]["total"][month_name][
                                "operation_id"
                            ] = operation.id
                            arr_keep_y["category"][2]["total"][month_name][
                                "chek"
                            ] = True
                        elif operation.between_bank.name == "на квартальную премию":

                            name_to_find = "на квартальную премию"
                            item = next(
                                (
                                    x
                                    for x in arr_summ_to_persent_y["category"]
                                    if x["name"] == name_to_find
                                ),
                                None,
                            )
                            if item:
                                item["total"][month_name][
                                    "amount_month_chek"
                                ] += operation.amount
                                item["total"][month_name]["operation_id"] = operation.id
                                item["total"][month_name]["chek"] = True

                        elif operation.between_bank.name == "КВ с $":

                            name_to_find = "КВ с $"
                            item = next(
                                (
                                    x
                                    for x in arr_summ_to_persent_y["category"]
                                    if x["name"] == name_to_find
                                ),
                                None,
                            )
                            if item:
                                item["total"][month_name][
                                    "amount_month_chek"
                                ] += operation.amount
                                item["total"][month_name]["operation_id"] = operation.id
                                item["total"][month_name]["chek"] = True

                # операции ВНУТРЕННИЕ СЧЕТА
                if operation.operaccount:
                    id_operacc_categ = get_id_categ_oper(operation.operaccount.category)
                    arr_inside_all_y["category"][1]["group"][id_operacc_categ][
                        month_name
                    ]["amount_month"] += operation.amount
                    arr_inside_all_y["category"][1]["total"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                    arr_inside_all_y["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                elif operation.salary and operation.employee:
                    pass
                    # 10 число в след месяц
                    if operation.salary.id == 1:
                        month_name = MONTHS_RU[operation.data.month - 2]
                        if (
                            month_name
                            in arr_inside_all_y["category"][0]["total"]["total"]
                        ):
                            arr_inside_all_y["category"][0]["total"]["total"][
                                month_name
                            ]["amount_month"] += operation.amount
                            arr_inside_all_y["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount

                    # не 10 число обычно
                    else:
                        arr_inside_all_y["category"][0]["total"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_inside_all_y["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

            # разные общие суммы
            for i, month in enumerate(months_year):

                # ПОСТУПЛЕНИЯ-СУБПОДРЯД (реальный доход)
                in_sum = (
                    arr_in_y["total_category"]["total"]
                    .get(month, {})
                    .get("amount_month", 0)
                )

                out_sum = (
                    arr_out_y["total_category"]["total"]
                    .get(month, {})
                    .get("amount_month", 0)
                )

                diff_in_out = in_sum - out_sum
                if month not in arr_in_out_all_y["category"][0]["total"]:
                    arr_in_out_all_y["category"][0]["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                arr_in_out_all_y["category"][0]["total"][month][
                    "amount_month"
                ] = diff_in_out
                # # ПРИБЫЛЬ 1% ЦРП 5%
                in_out_all_crp = (
                    diff_in_out
                    * arr_in_out_all_y["category"][1]["total"][month]["percent"]
                    / 100
                )
                arr_in_out_all_y["category"][1]["total"][month][
                    "amount_month"
                ] = in_out_all_crp

                # КВ 0,5 % ЦРП 50%
                in_out_all_crp_kv = (
                    diff_in_out
                    * arr_in_out_all_y["category"][2]["total"][month]["percent"]
                    / 100
                )
                arr_in_out_all_y["category"][2]["total"][month][
                    "amount_month"
                ] = in_out_all_crp_kv

                # ПРОВЕРКА ОБЩИЙ ДОХОД - РАСХОД - КВ И ТД B9-B19-B22-B23-B28-B34-B24
                all_oper_and_salary = arr_inside_all_y["total_category"]["total"][
                    month
                ]["amount_month"]
                bonus = arr_in_out_all_y["category"][3]["total"][month]["amount_month"]
                all_chek = (
                    diff_in_out
                    - in_out_all_crp
                    - in_out_all_crp_kv
                    - all_oper_and_salary
                    - bonus
                )
                arr_real_diff_y["total"][month]["amount_month"] = all_chek

                # # БЛОК ПРЦЕНЫ СОБСТВЕННИКУ И ВЛАДЕЛЬЦУ
                # # на квартальную премию собственникам

                if arr_summ_to_persent_y["category"][0]["total"][month]["chek"] == True:
                    to_kvartal_bonus = arr_summ_to_persent_y["category"][0]["total"][
                        month
                    ]["amount_month_chek"]
                else:
                    to_kvartal_bonus = (
                        in_out_all_crp
                        * arr_summ_to_persent_y["category"][0]["total"][month][
                            "percent"
                        ]
                        / 100
                    )
                arr_summ_to_persent_y["category"][0]["total"][month][
                    "amount_month"
                ] = to_kvartal_bonus

                # компенсация владельцу с ИП
                if arr_summ_to_persent_y["category"][1]["total"][month]["chek"] == True:
                    to_boss = arr_summ_to_persent_y["category"][1]["total"][month][
                        "amount_month_chek"
                    ]
                else:
                    to_boss = (
                        in_out_all_crp_kv
                        * arr_summ_to_persent_y["category"][1]["total"][month][
                            "percent"
                        ]
                        / 100
                    )
                arr_summ_to_persent_y["category"][1]["total"][month][
                    "amount_month"
                ] = to_boss

                # В ХРАНИЛИЩЕ:
                # остаток $ =B9-B19-B28-B34-B22-B23-B24
                to_last_after = all_chek
                if arr_keep_y["category"][0]["total"][month]["chek"]:
                    # заполненно из операций
                    pass
                else:
                    arr_keep_y["category"][0]["total"][month][
                        "amount_month"
                    ] = to_last_after

                # остаток ПРИБЫЛЬ 1% ЦРП 5%
                after_prs_crp = in_out_all_crp - to_kvartal_bonus
                if arr_keep_y["category"][1]["total"][month]["chek"]:
                    # заполненно из операций
                    pass
                else:
                    arr_keep_y["category"][1]["total"][month][
                        "amount_month"
                    ] = after_prs_crp

                # остаток КВ 0,5 % ЦРП 50%
                after_prs_kv = in_out_all_crp_kv - to_boss
                if arr_keep_y["category"][2]["total"][month]["chek"]:
                    # заполненно из операций
                    pass
                else:
                    arr_keep_y["category"][2]["total"][month][
                        "amount_month"
                    ] = after_prs_kv
                    # ИТОГО В ХРАНИЛИЩЕ из $:

                    total_storage = (
                        arr_keep_y["category"][0]["total"][month]["amount_month"]
                        + arr_keep_y["category"][1]["total"][month]["amount_month"]
                        + arr_keep_y["category"][2]["total"][month]["amount_month"]
                        + arr_keep_y["category"][3]["total"][month]["amount_month"]
                    )
                    arr_keep_y["total_category"]["total"][month][
                        "amount_month"
                    ] = total_storage

            arr_in_y = reverse_months_in_dict(arr_in_y)
            arr_out_y = reverse_months_in_dict(arr_out_y)
            arr_in_out_all_y = reverse_months_in_dict(arr_in_out_all_y)
            arr_real_diff_y = reverse_months_in_dict(arr_real_diff_y)
            arr_inside_all_y = reverse_months_in_dict(arr_inside_all_y)
            arr_summ_to_persent_y = reverse_months_in_dict(arr_summ_to_persent_y)
            arr_keep_y = reverse_months_in_dict(arr_keep_y)

            months_year = list(reversed(months_year))
            operations_by_year_mini = {}
            operations_actual = {
                "arr_in": arr_in_y,
                "arr_out": arr_out_y,
                "arr_in_out_all": arr_in_out_all_y,
                "arr_real_diff": arr_real_diff_y,
                "arr_inside_all": arr_inside_all_y,
                "arr_summ_to_persent": arr_summ_to_persent_y,
                "arr_keep": arr_keep_y,
                "months_current_year": months_year,
                "year": year,
                # "operations_by_year_mini":operations_by_year_mini
            }
            operations_by_year[year] = operations_actual

        operations_by_year = dict(sorted(operations_by_year.items(), reverse=True))

        return operations_by_year
    else:
        # Добавляем категории из CATEGORY_OPERACCOUNT
        for categ_oper in CATEGORY_OPERACCOUNT:

            arr_inside_all["category"][1]["group"][categ_oper[1]] = {}
            # Добавляем месяцы для каждой категории
            for i, month in enumerate(months_current_year):
                month_number = month_numbers[month]
                arr_inside_all["category"][1]["group"][categ_oper[1]][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

        # Добавляем месяцы
        for i, month in enumerate(months_current_year):
            month_number = month_numbers[month]
            arr_real_diff["total"][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
            }
            for inside_all in arr_inside_all["category"]:
                inside_all["total"]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
            # Для итогов поступления
            # внутренние счета расходы все
            arr_inside_all["total_category"]["total"][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
            }

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
            arr_out["category"][1]["group"]["зачисление на ИП для оплаты субподряда"][
                month
            ] = {
                "is_make_operations": True,
                "bank_out": between_id_nal_to_ip["bank_to"],
                "date_start": datetime.datetime(
                    year_now, MONTHS_RU.index(month) + 1, 1
                ),
                "operation_id": 0,
                "type_operations": "between",
                "between_id": between_id_nal_to_ip["id"],
                "amount_month": 0,
                "expected": 0,
            }
            arr_out["category"][1]["group"][
                "откладываем в хранилище на будущие расходы"
            ][month] = {
                "is_make_operations": True,
                "bank_out": between_id_nal_to_storage["bank_to"],
                "date_start": datetime.datetime(
                    year_now, MONTHS_RU.index(month) + 1, 1
                ),
                "operation_id": 0,
                "type_operations": "between",
                "between_id": between_id_nal_to_storage["id"],
                "amount_month": 0,
                "expected": 0,
            }

            # первый блок доход расход
            for in_out in arr_in_out_all["category"]:
                in_out["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                if in_out["name"] == "ПРИБЫЛЬ 1% ЦРП 5%":
                    in_out["total"][month]["is_make_operations"] = True
                    in_out["total"][month]["type_operations"] = "percent"

                    in_out["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    in_out["total"][month]["id_groupe"] = categ_percent_crp["id"]

                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_crp["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    in_out["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    in_out["total"][month]["operation_percent_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )
                elif in_out["name"] == "КВ 0,5 % ЦРП 50%":
                    in_out["total"][month]["is_make_operations"] = True
                    in_out["total"][month]["type_operations"] = "percent"

                    in_out["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    in_out["total"][month]["id_groupe"] = categ_percent_crp_kv["id"]

                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_crp_kv["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    in_out["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    in_out["total"][month]["operation_percent_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )
                elif in_out["name"] == "ПРЕМИИ":
                    in_out["total"][month]["is_make_operations"] = True
                    in_out["total"][month]["bank_out"] = (
                        between_id_for_nat_to_storage_bonus["bank_to"]
                    )
                    in_out["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    in_out["total"][month]["operation_id"] = 0
                    in_out["total"][month]["type_operations"] = "between"
                    in_out["total"][month]["between_id"] = (
                        between_id_for_nat_to_storage_bonus["id"]
                    )

            # В ХРАНИЛИЩЕ:
            arr_keep["total_category"]["total"][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
            }
            for keep_ip in arr_keep["category"]:
                if keep_ip["name"] == "остаток ПРИБЫЛЬ 1% ЦРП 5%":
                    keep_ip["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    keep_ip["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    keep_ip["total"][month]["is_make_operations"] = True

                    keep_ip["total"][month]["bank_out"] = between_id_nal_to_storage_crp[
                        "bank_to"
                    ]
                    keep_ip["total"][month]["operation_id"] = 0
                    keep_ip["total"][month]["type_operations"] = "between"
                    keep_ip["total"][month]["between_id"] = (
                        between_id_nal_to_storage_crp["id"]
                    )
                    keep_ip["total"][month]["amount_month_chek"] = 0
                    keep_ip["total"][month]["chek"] = False
                elif keep_ip["name"] == "остаток КВ 0,5 % ЦРП 50%":
                    keep_ip["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    keep_ip["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    keep_ip["total"][month]["is_make_operations"] = True

                    keep_ip["total"][month]["bank_out"] = between_id_nal_to_storage_kp[
                        "bank_to"
                    ]
                    keep_ip["total"][month]["operation_id"] = 0
                    keep_ip["total"][month]["type_operations"] = "between"
                    keep_ip["total"][month]["between_id"] = (
                        between_id_nal_to_storage_kp["id"]
                    )
                    keep_ip["total"][month]["amount_month_chek"] = 0
                    keep_ip["total"][month]["chek"] = False
                elif keep_ip["name"] == "остаток $":
                    keep_ip["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }
                    keep_ip["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    keep_ip["total"][month]["is_make_operations"] = True

                    keep_ip["total"][month]["bank_out"] = (
                        between_id_nal_to_storage_last["bank_to"]
                    )
                    keep_ip["total"][month]["operation_id"] = 0
                    keep_ip["total"][month]["type_operations"] = "between"
                    keep_ip["total"][month]["between_id"] = (
                        between_id_nal_to_storage_last["id"]
                    )
                    keep_ip["total"][month]["amount_month_chek"] = 0
                    keep_ip["total"][month]["chek"] = False
                elif keep_ip["name"] == "отложенные в хранилище на будущие расходы":
                    keep_ip["total"][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                    }

            for summ_to_persent in arr_summ_to_persent["category"]:
                summ_to_persent["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                if summ_to_persent["name"] == "на квартальную премию":
                    summ_to_persent["total"][month]["is_make_operations"] = True
                    summ_to_persent["total"][month]["type_operations"] = "percent"

                    summ_to_persent["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    summ_to_persent["total"][month]["id_groupe"] = (
                        categ_percent_to_boss["id"]
                    )
                    summ_to_persent["total"][month]["between_id"] = (
                        categ_percent_to_boss["category_between"]
                    )
                    summ_to_persent["total"][month]["bank_out"] = categ_percent_to_boss[
                        "category_between__bank_to"
                    ]
                    summ_to_persent["total"][month]["amount_month_chek"] = 0
                    summ_to_persent["total"][month]["chek"] = False

                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_to_boss["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    summ_to_persent["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    summ_to_persent["total"][month]["operation_percent_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )

                elif summ_to_persent["name"] == "КВ с $":
                    summ_to_persent["total"][month]["is_make_operations"] = True
                    summ_to_persent["total"][month]["type_operations"] = "percent"

                    summ_to_persent["total"][month]["date_start"] = datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    )
                    summ_to_persent["total"][month]["id_groupe"] = (
                        categ_percent_to_boss2["id"]
                    )
                    summ_to_persent["total"][month]["between_id"] = (
                        categ_percent_to_boss2["category_between"]
                    )
                    summ_to_persent["total"][month]["bank_out"] = (
                        categ_percent_to_boss2["category_between__bank_to"]
                    )
                    summ_to_persent["total"][month]["amount_month_chek"] = 0
                    summ_to_persent["total"][month]["chek"] = False

                    percent_obj = next(
                        (
                            item
                            for item in categ_percent_list
                            if item["category_id"] == categ_percent_to_boss2["id"]
                            and item["data"].month == MONTHS_RU.index(month) + 1
                            and item["data"].year == year_now
                        ),
                        None,
                    )
                    summ_to_persent["total"][month]["percent"] = (
                        percent_obj["percent"] if percent_obj else 0
                    )
                    summ_to_persent["total"][month]["operation_percent_id"] = (
                        percent_obj["id"] if percent_obj else 0
                    )

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
            elif operation.between_bank:
                if operation.bank_in == bank:
                    if (
                        operation.between_bank.name
                        == "зачисление на ИП для оплаты субподряда"
                    ):
                        arr_out["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_out["category"][1]["group"][
                            "зачисление на ИП для оплаты субподряда"
                        ][month_name]["amount_month"] += operation.amount
                        arr_out["category"][1]["group"][
                            "зачисление на ИП для оплаты субподряда"
                        ][month_name]["operation_id"] = operation.id
                    elif (
                        operation.between_bank.name
                        == "откладываем в хранилище на будущие расходы"
                    ):
                        arr_out["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_out["category"][1]["group"][
                            "откладываем в хранилище на будущие расходы"
                        ][month_name]["amount_month"] += operation.amount
                        arr_out["category"][1]["group"][
                            "откладываем в хранилище на будущие расходы"
                        ][month_name]["operation_id"] = operation.id

                        arr_keep["category"][3]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

                    elif operation.between_bank.name == "ПРЕМИИ":

                        name_to_find = "ПРЕМИИ"
                        item = next(
                            (
                                x
                                for x in arr_in_out_all["category"]
                                if x["name"] == name_to_find
                            ),
                            None,
                        )
                        if item:
                            item["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            item["total"][month_name]["operation_id"] = operation.id
                    elif operation.between_bank.name == "остаток $":
                        pass
                        arr_keep["category"][0]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_keep["category"][0]["total"][month_name][
                            "operation_id"
                        ] = operation.id
                        arr_keep["category"][0]["total"][month_name]["chek"] = True
                    elif operation.between_bank.name == "остаток ПРИБЫЛЬ 1% ЦРП 5%":
                        pass
                        arr_keep["category"][1]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_keep["category"][1]["total"][month_name][
                            "operation_id"
                        ] = operation.id
                        arr_keep["category"][1]["total"][month_name]["chek"] = True

                    elif operation.between_bank.name == "остаток КВ 0,5 % ЦРП 50%":
                        pass
                        arr_keep["category"][2]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_keep["category"][2]["total"][month_name][
                            "operation_id"
                        ] = operation.id
                        arr_keep["category"][2]["total"][month_name]["chek"] = True
                    elif operation.between_bank.name == "на квартальную премию":

                        name_to_find = "на квартальную премию"
                        item = next(
                            (
                                x
                                for x in arr_summ_to_persent["category"]
                                if x["name"] == name_to_find
                            ),
                            None,
                        )
                        if item:
                            item["total"][month_name][
                                "amount_month_chek"
                            ] += operation.amount
                            item["total"][month_name]["operation_id"] = operation.id
                            item["total"][month_name]["chek"] = True

                    elif operation.between_bank.name == "КВ с $":

                        name_to_find = "КВ с $"
                        item = next(
                            (
                                x
                                for x in arr_summ_to_persent["category"]
                                if x["name"] == name_to_find
                            ),
                            None,
                        )
                        if item:
                            item["total"][month_name][
                                "amount_month_chek"
                            ] += operation.amount
                            item["total"][month_name]["operation_id"] = operation.id
                            item["total"][month_name]["chek"] = True

            # операции ВНУТРЕННИЕ СЧЕТА
            if operation.operaccount:
                id_operacc_categ = get_id_categ_oper(operation.operaccount.category)
                arr_inside_all["category"][1]["group"][id_operacc_categ][month_name][
                    "amount_month"
                ] += operation.amount
                arr_inside_all["category"][1]["total"]["total"][month_name][
                    "amount_month"
                ] += operation.amount

                arr_inside_all["total_category"]["total"][month_name][
                    "amount_month"
                ] += operation.amount
            elif operation.salary and operation.employee:
                pass
                # 10 число в след месяц
                if operation.salary.id == 1:
                    month_name = MONTHS_RU[operation.data.month - 2]
                    if month_name in arr_inside_all["category"][0]["total"]["total"]:
                        arr_inside_all["category"][0]["total"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                        arr_inside_all["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

                # не 10 число обычно
                else:
                    arr_inside_all["category"][0]["total"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                    arr_inside_all["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

        # разные общие суммы
        for i, month in enumerate(months_current_year):

            # ПОСТУПЛЕНИЯ-СУБПОДРЯД (реальный доход)
            in_sum = (
                arr_in["total_category"]["total"].get(month, {}).get("amount_month", 0)
            )

            out_sum = (
                arr_out["total_category"]["total"].get(month, {}).get("amount_month", 0)
            )

            diff_in_out = in_sum - out_sum
            if month not in arr_in_out_all["category"][0]["total"]:
                arr_in_out_all["category"][0]["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
            arr_in_out_all["category"][0]["total"][month]["amount_month"] = diff_in_out
            # # ПРИБЫЛЬ 1% ЦРП 5%
            in_out_all_crp = (
                diff_in_out
                * arr_in_out_all["category"][1]["total"][month]["percent"]
                / 100
            )
            arr_in_out_all["category"][1]["total"][month][
                "amount_month"
            ] = in_out_all_crp

            # КВ 0,5 % ЦРП 50%
            in_out_all_crp_kv = (
                diff_in_out
                * arr_in_out_all["category"][2]["total"][month]["percent"]
                / 100
            )
            arr_in_out_all["category"][2]["total"][month][
                "amount_month"
            ] = in_out_all_crp_kv

            # ПРОВЕРКА ОБЩИЙ ДОХОД - РАСХОД - КВ И ТД B9-B19-B22-B23-B28-B34-B24
            all_oper_and_salary = arr_inside_all["total_category"]["total"][month][
                "amount_month"
            ]
            bonus = arr_in_out_all["category"][3]["total"][month]["amount_month"]
            all_chek = (
                diff_in_out
                - in_out_all_crp
                - in_out_all_crp_kv
                - all_oper_and_salary
                - bonus
            )
            arr_real_diff["total"][month]["amount_month"] = all_chek

            # # БЛОК ПРЦЕНЫ СОБСТВЕННИКУ И ВЛАДЕЛЬЦУ
            # # на квартальную премию собственникам

            if arr_summ_to_persent["category"][0]["total"][month]["chek"] == True:
                to_kvartal_bonus = arr_summ_to_persent["category"][0]["total"][month][
                    "amount_month_chek"
                ]
            else:
                to_kvartal_bonus = (
                    in_out_all_crp
                    * arr_summ_to_persent["category"][0]["total"][month]["percent"]
                    / 100
                )
            arr_summ_to_persent["category"][0]["total"][month][
                "amount_month"
            ] = to_kvartal_bonus

            # компенсация владельцу с ИП
            if arr_summ_to_persent["category"][1]["total"][month]["chek"] == True:
                to_boss = arr_summ_to_persent["category"][1]["total"][month][
                    "amount_month_chek"
                ]
            else:
                to_boss = (
                    in_out_all_crp_kv
                    * arr_summ_to_persent["category"][1]["total"][month]["percent"]
                    / 100
                )
            arr_summ_to_persent["category"][1]["total"][month]["amount_month"] = to_boss

            # В ХРАНИЛИЩЕ:
            # остаток $ =B9-B19-B28-B34-B22-B23-B24
            to_last_after = all_chek
            if arr_keep["category"][0]["total"][month]["chek"]:
                # заполненно из операций
                pass
            else:
                arr_keep["category"][0]["total"][month]["amount_month"] = to_last_after

            # остаток ПРИБЫЛЬ 1% ЦРП 5%
            after_prs_crp = in_out_all_crp - to_kvartal_bonus
            if arr_keep["category"][1]["total"][month]["chek"]:
                # заполненно из операций
                pass
            else:
                arr_keep["category"][1]["total"][month]["amount_month"] = after_prs_crp

            # остаток КВ 0,5 % ЦРП 50%
            after_prs_kv = in_out_all_crp_kv - to_boss
            if arr_keep["category"][2]["total"][month]["chek"]:
                # заполненно из операций
                pass
            else:
                arr_keep["category"][2]["total"][month]["amount_month"] = after_prs_kv
                # ИТОГО В ХРАНИЛИЩЕ из $:

                total_storage = (
                    arr_keep["category"][0]["total"][month]["amount_month"]
                    + arr_keep["category"][1]["total"][month]["amount_month"]
                    + arr_keep["category"][2]["total"][month]["amount_month"]
                    + arr_keep["category"][3]["total"][month]["amount_month"]
                )
                arr_keep["total_category"]["total"][month][
                    "amount_month"
                ] = total_storage

        return (
            arr_in,
            arr_out,
            arr_in_out_all,
            arr_real_diff,
            arr_inside_all,
            arr_summ_to_persent,
            arr_keep,
        )


def get_operations_by_year_mini(operations_by_year, key_arr=None):
    """
    Формирует словарь с той же структурой, что и operations_actual,
    но внутри только суммы за год по категориям, без детализации по месяцам.
    Ключи категорий: "name (сумма_за_год)".
    """

    def sum_category_group(group):
        result = {}
        for name, data in group.items():
            # Проверяем, является ли data словарем с месяцами или вложенной структурой
            if isinstance(data, dict):
                # Проверяем, есть ли в data месяцы (например, "январь", "февраль" и т.д.)
                has_months = any(
                    isinstance(month_data, dict) and "amount_month" in month_data
                    for month_data in data.values()
                )

                if has_months:
                    # Это месяцы, суммируем их
                    total = 0
                    for month_data in data.values():
                        if isinstance(month_data, dict):
                            total += month_data.get("amount_month", 0)
                    result[name] = total
                else:
                    # Это вложенная структура (например, SEO содержит ИП Галаев, Другое)
                    nested_result = {}
                    for sub_name, sub_data in data.items():
                        if isinstance(sub_data, dict):
                            sub_total = 0
                            for month_data in sub_data.values():
                                if isinstance(month_data, dict):
                                    sub_total += month_data.get("amount_month", 0)
                            nested_result[sub_name] = sub_total
                    result[name] = nested_result
            else:
                # Если это не словарь, просто копируем значение
                result[name] = data
        return result

    def sum_category_list(category_list, use_december_for_balance=False):
        result = []
        for cat in category_list:
            new_cat = {"name": cat.get("name", "")}
            if "group" in cat:
                new_cat["group"] = sum_category_group(cat["group"])
            if "total" in cat:
                if isinstance(cat["total"], dict):
                    # Проверяем, есть ли в total поля name и total (структура для arr_inside_all)
                    if "name" in cat["total"] and "total" in cat["total"]:
                        # Это структура с name и total (например, "ВЫПЛАЧЕННЫЕ НАЛОГИ (без УСН)")
                        total_sum = sum(
                            month_data.get("amount_month", 0)
                            for month_data in cat["total"]["total"].values()
                            if isinstance(month_data, dict)
                        )
                        new_cat["total"] = {
                            "name": cat["total"]["name"],
                            "total": total_sum,
                        }
                    else:
                        # Это обычный словарь с месяцами
                        if (
                            use_december_for_balance
                            and cat.get("name")
                            == "ОСТАТОК на Р/С на конец месяца (после уплаты УСН и вывода остатков)"
                        ):
                            # Для остатка на Р/С используем значение за декабрь
                            total = get_december_value(cat["total"])
                        else:
                            # Для остальных категорий суммируем все месяцы
                            total = sum(
                                month_data.get("amount_month", 0)
                                for month_data in cat["total"].values()
                                if isinstance(month_data, dict)
                            )
                        new_cat["total"] = total
                elif isinstance(cat["total"], (int, float)):
                    new_cat["total"] = cat["total"]
                else:
                    try:
                        new_cat["total"] = float(cat["total"])
                    except Exception:
                        new_cat["total"] = 0
            result.append(new_cat)
        return result

    def sum_total_category(total_category):
        if "total" in total_category:
            if isinstance(total_category["total"], dict):
                total = sum(
                    month_data.get("amount_month", 0)
                    for month_data in total_category["total"].values()
                    if isinstance(month_data, dict)
                )
            elif isinstance(total_category["total"], (int, float)):
                total = total_category["total"]
            else:
                try:
                    total = float(total_category["total"])
                except Exception:
                    total = 0
            return {"total": total, "name": total_category.get("name", "")}
        return {}

    def get_december_value(total_dict):
        """
        Получает значение за декабрь (последний месяц года) из словаря total
        """
        if not isinstance(total_dict, dict):
            return 0

        # Ищем декабрь (месяц 12) или последний доступный месяц
        december_value = 0
        last_month_value = 0

        for month_key, month_data in total_dict.items():
            if isinstance(month_data, dict) and "amount_month" in month_data:
                month_value = month_data.get("amount_month", 0)
                # Если это декабрь (месяц 12)
                if month_key == "12" or month_key == 12:
                    december_value = month_value
                # Сохраняем последнее значение для случая, если декабрь не найден
                last_month_value = month_value

        # Возвращаем значение декабря, если найдено, иначе последнее значение
        return december_value if december_value != 0 else last_month_value

    operations_by_year_mini = {}
    for year, data in operations_by_year.items():
        mini = {}
        for key in key_arr:
            block = data.get(key, {})
            mini_block = {}
            mini_block["name"] = block.get(
                "name", ""
            )  # Добавлено: переносим название блока
            if "category" in block:
                # Для arr_in_out_after_all_total используем логику декабря для остатка на Р/С
                use_december_for_balance = key == "arr_in_out_after_all_total"
                mini_block["category"] = sum_category_list(
                    block["category"], use_december_for_balance
                )
            if "total_category" in block:
                mini_block["total_category"] = sum_total_category(
                    block["total_category"]
                )
            if "total" in block and isinstance(block["total"], dict):
                # Для arr_start_month и arr_end_month берем значение за декабрь
                if key in ["arr_start_month", "arr_end_month"]:
                    total = get_december_value(block["total"])
                else:
                    # Для остальных массивов берем сумму всех месяцев
                    total = sum(
                        month_data.get("amount_month", 0)
                        for month_data in block["total"].values()
                        if isinstance(month_data, dict)
                    )
                mini_block["total"] = total
            mini[key] = mini_block
        mini["months_current_year"] = data.get("months_current_year", [])
        mini["year"] = year
        operations_by_year_mini[year] = mini
    return operations_by_year_mini


def fill_operations_arrays_keep_banking(
    arr_start_month,
    arr_in,
    arr_out,
    arr_stop_month_bank,
    arr_bonus_all,
    CATEGORY_OPERACCOUNT,
    months_current_year,
    month_numbers,
    year_now,
    operations,
    bank,
    cate_oper_beetwen_by_name,
    is_old_oper=False,
    old_oper_arr=None,
):
    between_id_to_ooo = cate_oper_beetwen_by_name.get("зачисление на ООО")
    between_id_to_ip = cate_oper_beetwen_by_name.get("зачисление на ИП")
    # Добавляем месяцы
    for i, month in enumerate(months_current_year):
        month_number = month_numbers[month]
        # рс на анчало меясца
        arr_start_month["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
        }
        arr_stop_month_bank["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
        }

        arr_in["total_category"]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
            "is_make_operations": False,
        }

        for category in arr_in["category"]:
            category["total"][month] = {
                "amount_month": 0,
                "month_number": MONTHS_RU.index(month) + 1,
            }

        arr_out["total_category"]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
            "is_make_operations": False,
        }
        for category in arr_out["category"]:

            if category["name"] == "зачисление на ООО":
                category["total"][month] = {
                    "is_make_operations": True,
                    "bank_out": between_id_to_ooo["bank_to"],
                    "date_start": datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "type_operations": "between",
                    "between_id": between_id_to_ooo["id"],
                    "amount_month": 0,
                    "expected": 0,
                }
            elif category["name"] == "зачисление на ИП":
                category["total"][month] = {
                    "is_make_operations": True,
                    "bank_out": between_id_to_ip["bank_to"],
                    "date_start": datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "type_operations": "between",
                    "between_id": between_id_to_ip["id"],
                    "amount_month": 0,
                    "expected": 0,
                }
            elif category["name"] == "покупки/траты":
                category["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": True,
                    "bank_out": 5,
                    "date_start": datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                }
            else:
                category["total"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }

        for category in arr_bonus_all["category"]:
            if category["name"] == "на квартальные премии 1:":
                category["group"]["на начало месяца"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                category["group"]["с $"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                category["group"]["с ООО -> ИП"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                category["group"]["на выплату премий (раз в квартал)"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                category["group"]["на конец месяца"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
            elif category["name"] == "на квартальные премии 2:":
                category["group"]["на начало месяца"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                category["group"]["с $"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                category["group"]["с ООО -> ИП"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                category["group"]["на выплату премий"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
                category["group"]["на конец месяца"][month] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                }
            
            
        arr_bonus_all["total_category"]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
        }
        
    # распределение операций
    for operation in operations:
        month_name = MONTHS_RU[operation.data.month - 1]
        prev_month = (
            MONTHS_RU[operation.data.month] if operation.data.month < 12 else None
        )
        is_prev_month = prev_month in months_current_year if prev_month else False

        # операции прихода из услуг(остатки бюджетов)
        if operation.monthly_bill and operation.suborder is None:
            # поступления по договорам услуг
            pass

        elif operation.salary and operation.employee:
            print(operation)
            if operation.salary.name == "Возврат долга":
                name_to_find = "возврат долга"
                item = next(
                    (x for x in arr_in["category"] if x["name"] == name_to_find),
                    None,
                )
                if item:
                    item["total"][month_name]["amount_month"] += operation.amount
                    item["total"][month_name]["operation_id"] = operation.id
                    arr_in["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
            if operation.salary.name == "Выдано в долг":
                name_to_find = "в долг"
                item = next(
                    (x for x in arr_out["category"] if x["name"] == name_to_find),
                    None,
                )
                print(item)
                if item:
                    item["total"][month_name]["amount_month"] += operation.amount
                    item["total"][month_name]["operation_id"] = operation.id
                    arr_out["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

        elif operation.bank_in.id == 3:

            if operation.between_bank.name in [
                "остаток $",
                "остаток ПРИБЫЛЬ 1% ЦРП 5%",
                "остаток КВ 0,5 % ЦРП 50%",
            ]:

                name_to_find = "$"
                item = next(
                    (x for x in arr_in["category"] if x["name"] == name_to_find),
                    None,
                )
                if item:
                    item["total"][month_name]["amount_month"] += operation.amount
                    item["total"][month_name]["operation_id"] = operation.id
                    arr_in["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

        elif operation.bank_in.id == 2:
            if operation.between_bank.name in [
                "вывод остатков ООО в Хранилище",
            ]:

                name_to_find = "ИП"
                item = next(
                    (x for x in arr_in["category"] if x["name"] == name_to_find),
                    None,
                )
                if item:
                    item["total"][month_name]["amount_month"] += operation.amount
                    item["total"][month_name]["operation_id"] = operation.id
                    arr_in["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
            elif operation.between_bank.name in [
                "остаток ПРИБЫЛЬ 1% ЦРП 5%",
            ]:

                name_to_find = "ИП"
                item = next(
                    (x for x in arr_in["category"] if x["name"] == name_to_find),
                    None,
                )
                if item:
                    item["total"][month_name]["amount_month"] += operation.amount
                    item["total"][month_name]["operation_id"] = operation.id
                    arr_in["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
            elif operation.between_bank.name in [
                "остаток КВ 0,5 % ЦРП 50%",
            ]:

                name_to_find = "ИП"
                item = next(
                    (x for x in arr_in["category"] if x["name"] == name_to_find),
                    None,
                )
                if item:
                    item["total"][month_name]["amount_month"] += operation.amount
                    item["total"][month_name]["operation_id"] = operation.id
                    arr_in["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                    
            elif operation.between_bank.name in [
                "на квартальную премию собственникам",
            ]:
                print(operation)

                name_to_find = "с ООО -> ИП"
                group_dict = arr_bonus_all["category"][0]["group"]
                item = group_dict.get(name_to_find)
                if item:
                    # В группах премий структура: group_name -> {month_name: {...}}
                    item[month_name]["amount_month"] += operation.amount
                    item[month_name]["operation_id"] = operation.id
                    arr_bonus_all["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
            
            elif operation.between_bank.name in [
                "ПРЕМИИ",
            ]:
                print(operation)

                name_to_find = "с ООО -> ИП"
                group_dict = arr_bonus_all["category"][1]["group"]
                item = group_dict.get(name_to_find)
                if item:
                    # В группах премий структура: group_name -> {month_name: {...}}
                    item[month_name]["amount_month"] += operation.amount
                    item[month_name]["operation_id"] = operation.id
                    arr_bonus_all["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

        elif operation.bank_in.id == 4:
            if operation.between_bank:
                if operation.between_bank.name in [
                    "зачисление на ООО",
                ]:

                    name_to_find = "зачисление на ООО"
                    item = next(
                        (x for x in arr_out["category"] if x["name"] == name_to_find),
                        None,
                    )
                    if item:
                        item["total"][month_name]["amount_month"] += operation.amount
                        item["total"][month_name]["operation_id"] = operation.id
                        arr_out["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
                elif operation.between_bank.name in [
                    "зачисление на ИП",
                ]:

                    name_to_find = "зачисление на ИП"
                    item = next(
                        (x for x in arr_out["category"] if x["name"] == name_to_find),
                        None,
                    )
                    if item:
                        item["total"][month_name]["amount_month"] += operation.amount
                        item["total"][month_name]["operation_id"] = operation.id
                        arr_out["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount
            else:
                if operation.bank_to.id == 5 and operation.salary == None:

                    name_to_find = "покупки/траты"
                    item = next(
                        (x for x in arr_out["category"] if x["name"] == name_to_find),
                        None,
                    )
                    if item:
                        item["total"][month_name]["amount_month"] += operation.amount
                        item["total"][month_name]["operation_id"] = operation.id
                        arr_out["total_category"]["total"][month_name][
                            "amount_month"
                        ] += operation.amount

    # разные общие суммы
    for i, month in enumerate(months_current_year):
        total_in = arr_in["total_category"]["total"][month]["amount_month"]
        total_out = arr_out["total_category"]["total"][month]["amount_month"]

        # ИТОГО Накопительные счета БЕЗ ПРЕМИЙ
        for i, month in enumerate(months_current_year):
            if i + 1 < len(months_current_year):
                month_prev = months_current_year[i + 1]
                prev_all_sum_month = arr_stop_month_bank["total"][month_prev][
                    "amount_month"
                ]
            else:
                # Для самого последнего месяца (например, "Январь") — остаток на конец декабря прошлого года, если есть
                prev_all_sum_month = 0
                if old_oper_arr:
                    prev_year = year_now - 1

                    last_month = "Декабрь"
                    prev_year_data = old_oper_arr.get(prev_year)
                    if prev_year_data:
                        try:
                            arr_stop_month_bank["total"][month]["amount_month"]
                            category_list = prev_year_data["arr_end_month_ip"][
                                "category"
                            ]
                            prev_all_sum_month = prev_year_data["arr_end_month_ip"][
                                "total"
                            ][last_month]["amount_month"]

                        except Exception as e:
                            print(
                                "Ошибка при доступе к остатку прошлого года (old_oper_arr):",
                                e,
                            )
                            prev_all_sum_month = 0

            all_sum_month = total_in - total_out + prev_all_sum_month

            arr_stop_month_bank["total"][month]["amount_month"] = all_sum_month

        # НАКОПИТЕЛЬНЫЕ СЧЕТА И НАЛИЧНЫЕ на начало месяца
        # получить следующий месяц
        for i, month in enumerate(months_current_year):
            if i == len(months_current_year) - 1:
                # Для самого последнего месяца (например, "Январь") — остаток на конец декабря прошлого года, если есть
                last_balance = 0
                if old_oper_arr:
                    prev_year = year_now - 1
                    last_month = "Декабрь"
                    prev_year_data = old_oper_arr.get(prev_year)

                    if prev_year_data:
                        try:
                            category_list = prev_year_data[
                                "arr_in_out_after_all_total"
                            ]["category"]
                            last_balance = category_list[3]["total"][last_month][
                                "amount_month"
                            ]
                        except Exception as e:
                            print(
                                "Ошибка при доступе к остатку прошлого года (old_oper_arr):",
                                e,
                            )
                            last_balance = 0
                arr_start_month["total"][month]["amount_month"] = last_balance
            else:
                next_month = months_current_year[i + 1]
                arr_start_month["total"][month]["amount_month"] = arr_stop_month_bank[
                    "total"
                ][next_month]["amount_month"]

    return arr_start_month, arr_in, arr_out, arr_bonus_all


def fill_operations_arrays_salary(
    employees,
    operations,
    operations_old,
    months_current_year,
    month_numbers,
    year_now,
    arr_ooo,
    arr_nal,
    arr_bonus,
    arr_lend,
    all_categories_qs,
    all_categories_bank,
    arr_total_employee,
    categ_percent_kv_nal,
    categ_percent_kv_ip,
    categ_percent_list,
    arr_total_salary,
    cate_oper_beetwen_by_name,
    operations_bonus,
    arr_total_bonus,
    percent_employee_data,
    categ_emploue_percent_list,
):
    between_id_nal_to_bonus = cate_oper_beetwen_by_name.get("КВ с $")
    print(categ_percent_list, "categ_percent_list")
    print(categ_percent_kv_nal, "categ_percent_kv_nal")
    print(categ_percent_kv_ip, "categ_percent_kv_ip")
    print(categ_emploue_percent_list, "categ_emploue_percent_list")
    year = year_now
    for i, month in enumerate(months_current_year):
        month_number = month_numbers[month]
        arr_total_employee["total"][month] = {
            "amount_month": 0,
            "month_number": f"{month_number:02d}",
            "is_make_operations": False,
        }
        # arr_nal
        arr_nal["total_category"]["total"][month] = {
            "amount_month": 0,
            "month_number": f"{month_number:02d}",
            "is_make_operations": False,
        }
        for category in arr_nal["category"]:
            category["total"][month] = {
                "is_make_operations": True,
                "bank_out": 5,
                "bank_in": 3,
                "date_start": datetime.datetime(
                    year_now, MONTHS_RU.index(month) + 1, 1
                ),
                "operation_id": 0,
                # "type_operations": "between",
                # "between_id": 3,
                "amount_month": 0,
                "expected": 0,
            }
        # arr_ooo
        arr_ooo["total_category"]["total"][month] = {
            "amount_month": 0,
            "month_number": f"{month_number:02d}",
            "is_make_operations": False,
        }
        for category in arr_ooo["category"]:
            category["total"][month] = {
                "is_make_operations": True,
                "bank_out": 5,
                "date_start": datetime.datetime(
                    year_now, MONTHS_RU.index(month) + 1, 1
                ),
                "operation_id": 0,
                "bank_in": 1,
                # "type_operations": "between",
                # "between_id": 3,
                "amount_month": 0,
                "expected": 0,
            }

        # arr_lend
        arr_lend["total_category"]["total"][month] = {
            "amount_month": 0,
            "month_number": f"{month_number:02d}",
            "is_make_operations": False,
        }
        for category in arr_lend["category"]:
            category["total"][month] = {
                "is_make_operations": True,
                "bank_out": 5,
                "date_start": datetime.datetime(
                    year_now, MONTHS_RU.index(month) + 1, 1
                ),
                "operation_id": 0,
                "bank_in": 1,
                # "type_operations": "between",
                # "between_id": 3,
                "amount_month": 0,
                "expected": 0,
            }

        # arr_bonus
        arr_bonus["total_category"]["total"][month] = {
            "amount_month": 0,
            "month_number": f"{month_number:02d}",
            "is_make_operations": False,
        }
        for category in arr_bonus["category"]:
            if category["name"] == "квартальная премия":
                category["total"][month] = {
                    "is_make_operations": True,
                    "bank_out": 5,
                    "date_start": datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "bank_in": 1,
                    # "type_operations": "between",
                    # "between_id": 3,
                    "amount_month": 0,
                    "expected": 0,
                }
            elif category["name"] == "КВ $":
                category["total"][month] = {
                    "percent": 0,
                    "id_groupe": categ_percent_kv_nal["id"],
                    "between_id": categ_percent_kv_nal["category_between__bank_to"],
                    "is_make_operations": True,
                    "bank_out": 5,
                    "date_start": datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "bank_in": 1,
                    # "type_operations": "between",
                    # "between_id": 3,
                    "amount_month": 0,
                    "expected": 0,
                    "amount_month_chek": 0,
                    "chek": False,
                }
                # percent_obj = next(
                #     (
                #         item
                #         for item in categ_percent_list
                #         if item["category_id"] == categ_percent_kv_nal["id"]
                #         and item["data"].month == MONTHS_RU.index(month) + 1
                #         and item["data"].year == year
                #     ),
                #     None,
                # )
                # category["total"][month]["percent"] = (
                #     percent_obj["percent"] if percent_obj else 0
                # )
                # category["total"][month]["operation_percent_id"] = (
                #     percent_obj["id"] if percent_obj else 0
                # )
            elif category["name"] == "КВ ИП":
                category["total"][month] = {
                    "percent": 0,
                    "id_groupe": categ_percent_kv_ip["id"],
                    "between_id": categ_percent_kv_ip["category_between__bank_to"],
                    "is_make_operations": True,
                    "bank_out": 5,
                    "date_start": datetime.datetime(
                        year_now, MONTHS_RU.index(month) + 1, 1
                    ),
                    "operation_id": 0,
                    "bank_in": 1,
                    "amount_month": 0,
                    "expected": 0,
                    "amount_month_chek": 0,
                    "chek": False,
                }
                # percent_obj = next(
                #     (
                #         item
                #         for item in categ_percent_list
                #         if item["category_id"] == categ_percent_kv_ip["id"]
                #         and item["data"].month == MONTHS_RU.index(month) + 1
                #         and item["data"].year == year
                #     ),
                #     None,
                # )
                # category["total"][month]["percent"] = (
                #     percent_obj["percent"] if percent_obj else 0
                # )
                # category["total"][month]["operation_percent_id"] = (
                #     percent_obj["id"] if percent_obj else 0
                # )

        # arr_total_salary
        for category in arr_total_salary["category"]:
            category["total"][month] = {
                "amount_month": 0,
                "month_number": f"{month_number:02d}",
                "is_make_operations": False,
            }

        # arr_total_bonus
        for category in arr_total_bonus["category"]:
            category["total"][month] = {
                "persent_bonus": 0,
                "summ_bonus": 0,
                "amount_month": 0,
                "month_number": f"{month_number:02d}",
                "is_make_operations": False,
            }

    # расчет премий общий
    for operation_bonus in operations_bonus:
        month_name = MONTHS_RU[operation_bonus.data.month - 1]
        if operation_bonus.between_bank.name == "КВ с $":
            arr_total_bonus["category"][0]["total"][month_name][
                "amount_month"
            ] += operation_bonus.amount
        elif operation_bonus.between_bank.name == "компенсация владельцу с ИП":
            arr_total_bonus["category"][1]["total"][month_name][
                "amount_month"
            ] += operation_bonus.amount
        elif operation_bonus.between_bank.name == "квартальная премия":
            arr_total_bonus["category"][2]["total"][month_name][
                "amount_month"
            ] += operation_bonus.amount
    
    arr_employee = {}
    for employee in employees:
        arr_employee[employee.id] = {
            "employee": employee,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "employee_id": employee.id,
            "data_salary": [
                copy.deepcopy(arr_total_employee),
                copy.deepcopy(arr_ooo),
                copy.deepcopy(arr_nal),
                copy.deepcopy(arr_bonus),
                copy.deepcopy(arr_lend),
            ],
        }
        employee_data = arr_employee[employee.id]
        
        


        # распределение операций
        for operation in operations:
            employee_id = operation.employee.id
            if operation.employee.id == employee.id:
                # Сначала ищем сотрудника
                employee_data = arr_employee[employee.id]

                category_name = operation.salary.name
                category_id = operation.salary.id
                group = None
                month_name = MONTHS_RU[operation.data.month - 1]
                prev_month = (
                    MONTHS_RU[operation.data.month]
                    if operation.data.month < 12
                    else None
                )
                is_prev_month = (
                    prev_month in months_current_year if prev_month else False
                )

                month_name = MONTHS_RU[operation.data.month - 1]
                prev_back_month = (
                    MONTHS_RU[operation.data.month - 2]
                    if operation.data.month < 12
                    else None
                )
                is_prev_back_month = (
                    prev_back_month in months_current_year if prev_back_month else False
                )

                name_to_find = category_name
                item = None
                parent_data_salary = None
                for data_salary in employee_data["data_salary"]:
                   
                    for x in data_salary["category"]:
                        if x["name"] == name_to_find:
                            item = x
                            parent_data_salary = data_salary
                            break
                    if item:
                        break

                if item:
                   
                    if item["name"]== "КВ $" or item["name"] == "КВ ИП" or item["name"] == "квартальная премия":
                      
                        item["total"][month_name][
                                    "amount_month_chek"
                                ] += operation.amount
                        item["total"][month_name]["operation_id"] = operation.id
                        item["total"][month_name]["chek"] = True
                        
            
                    else:
                        item["total"][month_name]["amount_month"] += operation.amount
                        item["total"][month_name]["operation_id"] = operation.id
                        
                        
                        
                if item and parent_data_salary:
                    if operation.salary.name == "Оф ЗП (10 число)":
                        if is_prev_back_month:
                            parent_data_salary["total_category"]["total"][
                                prev_back_month
                            ]["amount_month"] += operation.amount
                            employee_data["data_salary"][0]["total"][prev_back_month][
                                "amount_month"
                            ] += operation.amount
                            arr_total_salary["category"][0]["total"][prev_back_month][
                                "amount_month"
                            ] += operation.amount
                        else:
                            parent_data_salary["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            employee_data["data_salary"][0]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            arr_total_salary["category"][0]["total"][month_name][
                                "amount_month"
                            ] += operation.amount

                    else:
                        if parent_data_salary["name"] == "Долги":
                            pass
                        else:
                            parent_data_salary["total_category"]["total"][month_name][
                                "amount_month"
                            ] += operation.amount
                            employee_data["data_salary"][0]["total"][month_name][
                                "amount_month"
                            ] += operation.amount

                            if parent_data_salary["name"] == "ООО":
                                arr_total_salary["category"][0]["total"][month_name][
                                    "amount_month"
                                ] += operation.amount
                            elif parent_data_salary["name"] == "$":
                                arr_total_salary["category"][1]["total"][month_name][
                                    "amount_month"
                                ] += operation.amount
                            elif parent_data_salary["name"] == "Премии":
                                pass
                                if operation.salary.name == "КВ $":
                                    arr_total_salary["category"][2]["total"][
                                        month_name
                                    ]["amount_month"] += operation.amount
                                if operation.salary.name == "КВ ИП":
                                    arr_total_salary["category"][3]["total"][
                                        month_name
                                    ]["amount_month"] += operation.amount
                                if operation.salary.name == "квартальная премия":
                                    arr_total_salary["category"][4]["total"][
                                        month_name
                                    ]["amount_month"] += operation.amount

    # Рассчитываем накопительные остатки долга для каждого сотрудника
    for employee_id, employee_data in arr_employee.items():
        # Словарь для хранения накопительных остатков по месяцам
        debt_balances = {}

        # Сортируем месяцы в правильном порядке (от января к декабрю)
        months_ordered = []
        for month in range(1, 13):
            month_name = MONTHS_RU[month - 1]
            if month_name in months_current_year:
                months_ordered.append(month_name)

        # Рассчитываем 
        for i, month in enumerate(months_ordered):
            # Получаем предыдущий месяц (если это не первый месяц)
            prev_month = None
            next_month = None
            is_prev_month = False
            is_next_month = False
            if i > 0:
                prev_month = months_ordered[i - 1]
                is_prev_month = True
            if i < len(months_ordered) - 1:
                next_month = months_ordered[i + 1]
                is_next_month = True
                
            # Рассчитываем накопительные остатки долга
            # Получаем остаток предыдущего месяца
            prev_balance = debt_balances.get(prev_month, 0) if prev_month else 0

            # Получаем операции за текущий месяц
            debt_issued = 0
            debt_returned = 0

            for data_salary in employee_data["data_salary"]:
                if data_salary["name"] == "Долги":
                    for category in data_salary["category"]:
                        if (
                            category["name"] == "Выдано в долг"
                            and month in category["total"]
                        ):
                            debt_issued += category["total"][month]["amount_month"]

                        elif (
                            category["name"] == "Возврат долга"
                            and month in category["total"]
                        ):
                            debt_returned += category["total"][month]["amount_month"]

                        elif category["name"] == "Остаток долга":
                            pass

            # Рассчитываем текущий накопительный остаток
            current_balance = prev_balance + debt_issued - debt_returned
            current_balance = max(0, current_balance)  # Не даем остатку уйти в минус

            # Сохраняем остаток
            debt_balances[month] = current_balance

            # Обновляем total_category и категорию "Остаток долга" для группы "Долги"
            for data_salary in employee_data["data_salary"]:
                if data_salary["name"] == "Долги":
                    # Обновляем total_category
                    if month in data_salary["total_category"]["total"]:
                        data_salary["total_category"]["total"][month][
                            "amount_month"
                        ] = current_balance

                    # Обновляем категорию "Остаток долга"
                    for category in data_salary["category"]:
                        if (
                            category["name"] == "Остаток долга"
                            and month in category["total"]
                        ):
                            category["total"][month]["amount_month"] = current_balance

            arr_total_salary["category"][5]["total"][month][
                "amount_month"
            ] += current_balance
          
            # РАСЧЕТ ПРЕМИЙ СОТРУДНИКА
        #   КВ ИП10
            percent_obj = next(
            (
                item
                for item in categ_emploue_percent_list

                if item["category_id"] == categ_percent_kv_ip["id"]
                and item["data"].month == MONTHS_RU.index(month) + 1
                and item["data"].year == year
                and item["employee_id"] == employee_id
            ),
            None,
        )
            if percent_obj:
                print(percent_obj,"percent_obj")
                print(month,"month")
                 
                
                arr_total_bonus["category"][1]["total"][month]["persent_bonus"] += percent_obj["percent"]
                
                employee_data["data_salary"][3]["category"][1]["total"][month]["bank_in"] = categ_percent_kv_ip["bank"]
                employee_data["data_salary"][3]["category"][1]["total"][month]["percent"] = (
                    percent_obj["percent"] if percent_obj else 0
                )
                employee_data["data_salary"][3]["category"][1]["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )
                if is_next_month and next_month:
                    employee_data["data_salary"][3]["category"][1]["total"][next_month]["expected"] = employee_data["data_salary"][3]["category"][1]["total"][month]["percent"]
                
                # sum_kv_ip = (arr_total_bonus["category"][1]["total"][month]["amount_month"] / 100 )* percent_obj["percent"]
                # employee_data["data_salary"][3]["category"][1]["total"][month]["amount_month"] = sum_kv_ip
                
                if employee_data["data_salary"][3]["category"][1]["total"][month]["chek"] == True:
                    sum_kv_ip_to_front = employee_data["data_salary"][3]["category"][1]["total"][month]["amount_month_chek"]
                    arr_total_bonus["category"][1]["total"][month]["summ_bonus"] += sum_kv_ip_to_front
                else:
                    sum_kv_ip_to_front = (arr_total_bonus["category"][1]["total"][month]["amount_month"] / 100 )* percent_obj["percent"]
                employee_data["data_salary"][3]["category"][1]["total"][month]["amount_month"] = sum_kv_ip_to_front
                
                # РАСЧЕТ ПРЕМИЙ СОТРУДНИКА
        #   КВ ИП10
            percent_obj = next(
            (
                item
                for item in categ_emploue_percent_list

                if item["category_id"] == categ_percent_kv_nal["id"]
                and item["data"].month == MONTHS_RU.index(month) + 1
                and item["data"].year == year
                and item["employee_id"] == employee_id
            ),
            None,
        )
            if percent_obj:
                print(percent_obj,"percent_obj")
                print(month,"month")
                 
                
                arr_total_bonus["category"][1]["total"][month]["persent_bonus"] += percent_obj["percent"]
                
                employee_data["data_salary"][3]["category"][0]["total"][month]["bank_in"] = categ_percent_kv_nal["bank"]
                employee_data["data_salary"][3]["category"][0]["total"][month]["percent"] = (
                    percent_obj["percent"] if percent_obj else 0
                )
                employee_data["data_salary"][3]["category"][0]["total"][month]["operation_percent_id"] = (
                            percent_obj["id"] if percent_obj else 0
                        )
                if is_next_month and next_month:
                    employee_data["data_salary"][3]["category"][0]["total"][next_month]["expected"] = employee_data["data_salary"][3]["category"][1]["total"][month]["percent"]
                
                # sum_kv_ip = (arr_total_bonus["category"][1]["total"][month]["amount_month"] / 100 )* percent_obj["percent"]
                # employee_data["data_salary"][3]["category"][1]["total"][month]["amount_month"] = sum_kv_ip
                
                if employee_data["data_salary"][3]["category"][0]["total"][month]["chek"] == True:
                    sum_kv_nal_to_front = employee_data["data_salary"][3]["category"][0]["total"][month]["amount_month_chek"]
                    arr_total_bonus["category"][0]["total"][month]["summ_bonus"] += sum_kv_nal_to_front
                else:
                    sum_kv_nal_to_front = (arr_total_bonus["category"][1]["total"][month]["amount_month"] / 100 )* percent_obj["percent"]
                employee_data["data_salary"][3]["category"][1]["total"][month]["amount_month"] = sum_kv_nal_to_front
                
                


    

    return (arr_employee, arr_total_salary, arr_total_bonus)


def fill_operations_storage_servise( arr_service,
        year_now,
        months_current_year,
        month_numbers,
        operations,
    ):
    # ЗАПОЛНЕНИЕ МАССИВОВ ДАННЫМИ

    
    for i, month in enumerate(months_current_year):
        month_number = month_numbers[month]

        arr_service["category"][0]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
            "history_comment": [],
        }

    # распределение операций
    for operation in operations:
        month_name = MONTHS_RU[operation.data.month - 1]

        if operation.monthly_bill and operation.suborder is None:
            # поступления по договорам услуг
            arr_service["category"][0]["total"][month_name][
                "amount_month"
            ] += operation.amount
            h_c = f"Клиент {operation.monthly_bill.client.name} дата {operation.data} сумма {operation.amount} ₽"
            arr_service["category"][0]["total"][month_name]["history_comment"].append(h_c)

    return arr_service


def fill_operations_storage_servise_client(
        client_adv,
        year_now,
        months_current_year,
        month_numbers,
        operations,
        adv_service,
        bank,
    ):
    # ЗАПОЛНЕНИЕ МАССИВОВ ДАННЫМИ
    
    arr_client = {
        "client": client_adv,
        "contract": 0,
        "total_category_start": {
            "name": "на начало месяца",
            "total": {},
        },
        "total_category_last": {
            "name": "на конец месяца",
            "total": {},
        },
        "category": [
             {
                "name": "Приход",
                "total": {},
            },
            {
                "name": "Расход",
                "total": {},
            },
        ]
       
    } 
    
    arr_clients_all = []
    
    for i, month in enumerate(months_current_year):
        month_number = month_numbers[month]

        arr_client["category"][0]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
            "history_comment": [],
        }
        arr_client["category"][1]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
            "history_comment": [],
            "is_make_operations": True,
            "bank_out": 4,
            "date_start": datetime.datetime(
                    year_now, MONTHS_RU.index(month) + 1, 1
                ),
            "operation_id": 0,
            
        }
        arr_client["total_category_last"]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
        }
        arr_client["total_category_start"]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
             
        }
    
    for client in client_adv:
        # Копируем существующую структуру arr_client
        arr_client_copy = copy.deepcopy(arr_client)
        
        # Заменяем client на текущего клиента
        arr_client_copy["client"] = client
        arr_client_copy["contract"] = arr_client_copy["contract"] = client.contract_set.filter(service=adv_service)
        # Добавляем копию в общий массив
        arr_clients_all.append(arr_client_copy)

    print(arr_clients_all,"arr_clients_all")
    # распределение операций
    for operation in operations:
        month_name = MONTHS_RU[operation.data.month - 1]
        client_id = operation.employee.id
       
        if operation.employee.id == client_id and operation.bank == bank:
            print(operation,"operation")
        
            
            
    return arr_clients_all