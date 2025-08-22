# Инструкция по сборке macOS M2 приложения

## Что уже настроено ✅

1. **GitHub Actions workflow** - `.github/workflows/build-macos.yml`
2. **Спецификация PyInstaller** - `run_app_macos.spec`
3. **Requirements.txt** - `requirements.txt`
4. **Все необходимые файлы** для сборки

## Как использовать

### 1. Код уже загружен в GitHub ✅
- Репозиторий: `https://github.com/Shvechkova/Bookkeeping.git`
- Последний коммит: `Fix macOS build: remove .env dependency, fix apps modules, add build .env creation in GitHub Actions`

### 2. Запустите сборку вручную 🚀
- Перейдите в ваш репозиторий на GitHub
- Нажмите на вкладку **"Actions"**
- Найдите workflow **"Build macOS M2 Executable"**
- Нажмите **"Run workflow"** (зеленая кнопка)
- Выберите ветку (обычно main)
- Нажмите **"Run workflow"**

### 3. Дождитесь завершения и скачайте
- Следите за процессом в реальном времени
- Дождитесь зеленой галочки (успешное завершение)
- Нажмите на **"macos-m2-executable"**
- Скачайте артефакт
- Распакуйте архив
- Запустите `run_app.app`

## Что происходит в GitHub Actions

1. **Запуск на macOS runner** (macos-latest)
2. **Установка Python 3.12**
3. **Создание .env файла** с тестовыми настройками
4. **Установка зависимостей** из requirements.txt
5. **Сборка через PyInstaller** с run_app_macos.spec
6. **Создание .app bundle** для macOS
7. **Загрузка артефакта** для скачивания

## Если нужно изменить настройки

- Отредактируйте `run_app_macos.spec`
- Измените `.github/workflows/build-macos.yml`
- Сделайте коммит и push
- **Запустите сборку вручную** через "Run workflow"

## Структура готового приложения

```
dist/macos-m2/
└── run_app.app/
    └── Contents/
        ├── MacOS/
        │   └── run_app (исполняемый файл)
        └── Resources/ (все данные Django)
```

## Преимущества macOS сборки

- ✅ **Нативная производительность** на Apple Silicon (M2)
- ✅ **Красивый .app bundle** - как обычное macOS приложение
- ✅ **Автоматическая подпись** (если настроена)
- ✅ **Простая установка** - перетащить в Applications

## Важно знать

- 🔄 **Сборка НЕ запускается автоматически** при push
- 🚀 **Только ручной запуск** через "Run workflow"
- ⏱️ **Экономия времени** GitHub Actions (только когда нужно)
- 🎯 **Полный контроль** над процессом сборки
