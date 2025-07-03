from apps.bank.models import CATEGORY_OPERACCOUNT
from apps.core.models import LogsError, Logsinfo


def error_alert(error, location, info):
    error_alert = LogsError.objects.create(
           location=location, info=info
        )

def log_alert(error, location, info):
    error_alert = Logsinfo.objects.create(
           location=location, info=info
        )
    
def create_month_categ_persent():
    pass

def get_id_categ_oper(id_nalog):
    for categ_oper_for in CATEGORY_OPERACCOUNT:
        name = categ_oper_for[1]
        id = categ_oper_for[0]

        if id_nalog == id:
            return name
