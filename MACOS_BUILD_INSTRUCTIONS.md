# Инструкция по сборке macOS M2 приложения

## Что уже настроено ✅

1. **GitHub Actions workflow** - `.github/workflows/build-macos.yml`
2. **Спецификация PyInstaller** - `run_app_macos.spec`
3. **Requirements.txt** - `requirements.txt`
4. **Все необходимые файлы** для сборки

## Как использовать

### 1. Код уже загружен в GitHub ✅
- Репозиторий: `https://github.com/Shvechkova/Bookkeeping.git`
- Последний коммит: `Add macOS M2 build support with GitHub Actions workflow`

### 2. GitHub Actions автоматически запустится
- Перейдите в ваш репозиторий на GitHub
- Нажмите на вкладку **"Actions"**
- Найдите workflow **"Build macOS M2 Executable"**
- Дождитесь завершения (зеленая галочка)

### 3. Скачайте готовое приложение
- В завершенном workflow нажмите **"macos-m2-executable"**
- Скачайте артефакт
- Распакуйте архив
- Запустите `run_app.app`

## Что происходит в GitHub Actions

1. **Запуск на macOS runner** (macos-latest)
2. **Установка Python 3.12**
3. **Установка зависимостей** из requirements.txt
4. **Сборка через PyInstaller** с run_app_macos.spec
5. **Создание .app bundle** для macOS
6. **Загрузка артефакта** для скачивания

## Если нужно изменить настройки

- Отредактируйте `run_app_macos.spec`
- Измените `.github/workflows/build-macos.yml`
- Сделайте коммит и push
- GitHub Actions автоматически пересоберет приложение

## Структура готового приложения

```
dist/macos-m2/
└── run_app.app/
    └── Contents/
        ├── MacOS/
        │   └── run_app (исполняемый файл)
        └── Resources/ (все данные Django)
```
