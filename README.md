# Google API Project

Учебный проект по работе с Google Sheets API v4 и Google Drive API v3.

## Структура

```
training_spreadsheets.py  — Sheets API: создание, шаринг, запись
control_drive.py          — Drive API: листинг файлов, удаление
travel_budget/            — CLI-приложение (рефакторинг двух скриптов выше)
  services.py             — OAuth2 авторизация + константы сервисов
  main.py                 — argparse CLI с 5 командами
```

## Запуск

```bash
uv run python training_spreadsheets.py
uv run python control_drive.py

cd travel_budget
python main.py -ls                     # список таблиц
python main.py -c "Название, 50000"    # создать таблицу
python main.py -u "Описание, Тип, 2, 500, =C7*D7" -i <ID>  # обновить
```

## Требования

- Python 3.12+
- `oauth_client.json` в корне проекта (OAuth2 credentials)
- Первый запуск откроет браузер для авторизации
