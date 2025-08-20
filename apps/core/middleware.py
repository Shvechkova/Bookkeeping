from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Список URL, доступных без входа
        allowed_paths = [
            # reverse('login'),  # например, /login/
            reverse('admin:login'),
            # можно добавить logout, reset password и т.д.
        ]

        # Исключения: статика и медиа
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # Дополнительные пути без входа (если нужно)
        if request.path in allowed_paths or request.path.startswith('/admin/login'):
            return self.get_response(request)

        # Основная проверка: пользователь залогинен?
        if not request.user.is_authenticated:
            return redirect('admin:login')  # или reverse('login')

        # Если пользователь залогинен — доступ разрешён
        return self.get_response(request)