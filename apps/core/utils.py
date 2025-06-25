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