import os
import webbrowser
from threading import Timer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")


def open_browser():
    try:
        webbrowser.open("http://127.0.0.1:8000", new=2)
    except Exception:
        pass


def main():
    import django
    from waitress import serve
    from django.core.wsgi import get_wsgi_application

    django.setup()
    Timer(1.0, open_browser).start()
    serve(get_wsgi_application(), listen="127.0.0.1:8000")


if __name__ == "__main__":
    main()


