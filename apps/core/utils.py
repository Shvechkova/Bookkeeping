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

                    # Для переводов с ИП
                    arr_in_y["category"][1]["group"][
                        "перевод с ИП для оплаты субподряда"
                    ][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }

                    # Для переводов с $
                    arr_in_y["category"][1]["group"][
                        "перевод с $ для оплаты субподряда"
                    ][month] = {
                        "amount_month": 0,
                        "month_number": MONTHS_RU.index(month) + 1,
                        "is_make_operations": False,
                    }
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
            month_number = month_numbers[month]
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

                # Для переводов с ИП
                arr_in["category"][1]["group"]["перевод с ИП для оплаты субподряда"][
                    month
                ] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }

                # Для переводов с $
                arr_in["category"][1]["group"]["перевод с $ для оплаты субподряда"][
                    month
                ] = {
                    "amount_month": 0,
                    "month_number": MONTHS_RU.index(month) + 1,
                    "is_make_operations": False,
                }
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
            prev_month = MONTHS_RU[operation.data.month]

            if prev_month in months_current_year:
                is_prev_month = True
            else:
                is_prev_month = False

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
                # расходы по договорам услуг
                # Для SEO
                if operation.suborder.month_bill.service.name == "SEO":

                    if (
                        operation.suborder.category_employee
                        and operation.suborder.category_employee.name == "ИП Галаев"
                    ):
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
    old_oper_arr,
):
    categoru_nalog_fact = categoru_nalog.get(name="ФАКТИЧЕСКАЯ ОПЛАТА НАЛОГОВ")

    between_id_ip_to_mir = cate_oper_beetwen_by_name.get(
        "вывод $ для оплаты субподряда (вручную)"
    )
    between_id_for_ooo_ip_to_storage = cate_oper_beetwen_by_name.get(
        "вывод остатков ООО в Хранилище"
    )
    print(
        "between_id_ip_to_mir,between_id_for_ooo_ip_to_storage",
        between_id_ip_to_mir,
        between_id_for_ooo_ip_to_storage,
    )
    print(categ_percent_by_name)
    categ_percent_crp = categ_percent_by_name.get("ПРИБЫЛЬ 1% ЦРП 5%")
    categ_percent_crp_kv = categ_percent_by_name.get("КВ 20% ЦРП 50%")
    categ_percent_to_boss = categ_percent_by_name.get(
        "на квартальную премию собственникам"
    )
    categ_percent_to_boss2 = categ_percent_by_name.get("компенсация владельцу с ИП")

    print(
        "categ_percent_crp,categ_percent_crp_kv",
        categ_percent_crp,
        categ_percent_crp_kv,
        categ_percent_to_boss,
        categ_percent_to_boss2,
    )
    print("categ_percent_list", categ_percent_list)
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
            "date_start": datetime.datetime(year_now, MONTHS_RU.index(month) + 1, 1),
            "operation_id": 0,
            "type_operations": "between",
            "between_id": between_id_ip_to_mir["id"],
            "amount_month": 0,
            "expected": 0,
        }
        arr_out["category"][1]["group"]["вывод остатков ООО в Хранилище"][month] = {
            "is_make_operations": True,
            "bank_out": between_id_for_ooo_ip_to_storage["bank_to"],
            "date_start": datetime.datetime(year_now, MONTHS_RU.index(month) + 1, 1),
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
                    ),
                    None,
                )
                print(
                    "month:",
                    month,
                    "MONTHS_RU.index(month)+1:",
                    MONTHS_RU.index(month) + 1 if month in MONTHS_RU else "нет",
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

                percent_obj = next(
                    (
                        item
                        for item in categ_percent_list
                        if item["category_id"] == categ_percent_crp_kv["id"]
                        and item["data"].month == MONTHS_RU.index(month) + 1
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
                in_out_after["total"][month]["id_groupe"] = categoru_nalog_fact["id"]

        # В ХРАНИЛИЩЕ:
        arr_keep_ip["total_category"]["total"][month] = {
            "amount_month": 0,
            "month_number": MONTHS_RU.index(month) + 1,
        }
        for keep_ip in arr_keep_ip["category"]:
            pass

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
                summ_to_persent["total"][month]["id_groupe"] = categ_percent_to_boss[
                    "id"
                ]

                percent_obj = next(
                    (
                        item
                        for item in categ_percent_list
                        if item["category_id"] == categ_percent_to_boss["id"]
                        and item["data"].month == MONTHS_RU.index(month) + 1
                    ),
                    None,
                )
                print(
                    "month:",
                    month,
                    "MONTHS_RU.index(month)+1:",
                    MONTHS_RU.index(month) + 1 if month in MONTHS_RU else "нет",
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
                summ_to_persent["total"][month]["id_groupe"] = categ_percent_to_boss2[
                    "id"
                ]

                percent_obj = next(
                    (
                        item
                        for item in categ_percent_list
                        if item["category_id"] == categ_percent_to_boss2["id"]
                        and item["data"].month == MONTHS_RU.index(month) + 1
                    ),
                    None,
                )
                print(
                    "month:",
                    month,
                    "MONTHS_RU.index(month)+1:",
                    MONTHS_RU.index(month) + 1 if month in MONTHS_RU else "нет",
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
                elif operation.between_bank.name == "вывод остатков ООО в Хранилище":
                    arr_out["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount
                    arr_out["category"][1]["group"]["вывод остатков ООО в Хранилище"][
                        month_name
                    ]["amount_month"] += operation.amount
                    arr_out["category"][1]["group"]["вывод остатков ООО в Хранилище"][
                        month_name
                    ]["operation_id"] = operation.id

                    if is_prev_month:
                        arr_out["category"][1]["group"][
                            "вывод остатков ООО в Хранилище"
                        ][prev_month]["expected"] += operation.amount

            # приходящее между счетами
            if operation.bank_to == bank:
                if operation.between_bank.name == "перевод на ИП для оплаты субподряда":
                    arr_in["category"][1]["group"][
                        "перевод с ООО для оплаты субподряда"
                    ][month_name]["amount_month"] += operation.amount
                    arr_in["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                elif operation.between_bank.name == "ПРЕМИИ":
                    arr_in["category"][1]["group"]["на премии"][month_name][
                        "amount_month"
                    ] += operation.amount
                    arr_in["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                    arr_in_out_all["category"][2]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

                elif operation.between_bank.name == "ВЫВОД ОСТАТКОВ НА ИП + НАЛОГИ ИП":
                    arr_in["category"][1]["group"]["ПЕРЕВОД ОСТАТКОВ С ООО"][
                        month_name
                    ]["amount_month"] += operation.amount
                    arr_in["total_category"]["total"][month_name][
                        "amount_month"
                    ] += operation.amount

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
                            group["ООО прибыль ЦРП 5%"][month_name]["amount_month"] += v

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
        in_sum = arr_in["total_category"]["total"].get(month, {}).get("amount_month", 0)
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
        print(arr_in_out_all["category"][0])

        in_out_all_crp = (
            diff_in_out * arr_in_out_all["category"][0]["total"][month]["percent"] / 100
        )
        arr_in_out_all["category"][0]["total"][month]["amount_month"] = in_out_all_crp
        # КВ 20% ЦРП 50%

        in_out_all_crp_kv = (
            diff_in_out * arr_in_out_all["category"][1]["total"][month]["percent"] / 100
        )
        arr_in_out_all["category"][1]["total"][month][
            "amount_month"
        ] = in_out_all_crp_kv
        # всего выводим с ИП (премии+КВ+остатки)
        bonus = arr_in_out_all["category"][2]["total"][month]["amount_month"]
        all_out_check = bonus + in_out_all_crp_kv + in_out_all_crp
        arr_in_out_all["category"][3]["total"][month]["amount_month"] = all_out_check
        # ПРОВЕРКА ДОХОД-РАСХОД =B12-B23-B28-B27-B38-B40
        total_oper_and_nalog = arr_inside_all["total_category"]["total"][month][
            "amount_month"
        ]
        total_check = (
            diff_in_out - in_out_all_crp_kv - in_out_all_crp - total_oper_and_nalog
        )
        arr_in_out_after_all["category"][0]["total"][month][
            "amount_month"
        ] = total_check

        # ПРОВЕРКА =B12-B23-B28-B27-B38-B40 -    B29
        total_check_sver = total_check - bonus
        arr_in_out_all["category"][4]["total"][month]["amount_month"] = total_check_sver

        # ДОХОД-РАСХОД+отложенные налоги
        nalog = arr_inside_all["category"][1]["total"]["total"][month_name][
            "amount_month"
        ]
        total_check_sver_and_nalog = total_check - nalog
        arr_in_out_after_all["category"][1]["total"][month][
            "amount_month"
        ] = total_check_sver_and_nalog

        # ИТОГО В ХРАНИЛИЩЕ из $:
        total_to_storage = 777
        arr_keep_ip["total_category"]["total"][month]["amount_month"] = total_to_storage

        for i, month in enumerate(months_current_year):
                if i + 1 < len(months_current_year):
                    month_prev = months_current_year[i + 1]
                    prev_all_sum_month = 1
                    
                    # prev_all_sum_month = arr_in_out_after_all_total["category"][3][
                    #     "total"
                    # ][month_prev]["amount_month"]
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
                
                nalog_real =  arr_in_out_after_all["category"][2]["total"][month][
            "amount_month"
        ]
                all_sum_month = total_check_sver_and_nalog - nalog_real + prev_all_sum_month
                # all_sum_month = (
                #     diff_in_out_real - nalog_ycn - to_ip + prev_all_sum_month
                # )
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
                arr_start_month["total"][month]["amount_month"] = 333
                # (
                #     arr_in_out_after_all_total["category"][3]["total"][next_month][
                #         "amount_month"
                #     ]
                # )

    return (
        arr_in,
        arr_out,
        arr_real_diff,
        arr_in_out_all,
        arr_inside_all,
        arr_keep_ip,
        # arr_in_out_after_all,
        # arr_summ_to_persent,
        # arr_keep,
        # arr_end_month,
        # arr_start_month,
    )
