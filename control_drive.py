"""Управление файлами Google Drive через API v3."""

import os
from typing import Any

from google.auth.credentials import Credentials as BaseCredentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery

CREDENTIALS_FILE = 'oauth_client.json'
TOKEN_FILE = 'token.json'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]


def auth() -> tuple[Any, BaseCredentials]:
    """Авторизация в Google Drive API через OAuth2."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    service = discovery.build('drive', 'v3', credentials=creds)
    return service, creds


def get_list_obj(service: Any) -> dict:
    """Получение списка объектов на Google Drive."""
    response = service.files().list(
        q='mimeType="application/vnd.google-apps.spreadsheet"')
    return response.execute()


def clear_disk(service: Any, spreadsheets: list[dict]) -> None:
    """Удаление таблиц с Google Drive."""
    for spreadsheet in spreadsheets:
        response = service.files().delete(fileId=spreadsheet['id'])
        response.execute()


# Безопасный тест: создаём фейковую таблицу и удаляем только её
service, creds = auth()

# Создаём тестовую таблицу через Sheets API
sheets_service = discovery.build('sheets', 'v4', credentials=creds)
test_spreadsheet = sheets_service.spreadsheets().create(
    body={'properties': {'title': 'ТЕСТ_ДЛЯ_УДАЛЕНИЯ'}}).execute()
test_id = test_spreadsheet['spreadsheetId']
print(f'Создана тестовая таблица: {test_id}')

# Проверяем, что она появилась на диске
spreadsheets = get_list_obj(service)['files']
print(f'Таблиц на диске: {len(spreadsheets)}')

# Удаляем только тестовую таблицу
clear_disk(service, [{'id': test_id}])
print(f'Удалена тестовая таблица: {test_id}')

# Проверяем, что стало на одну меньше
spreadsheets = get_list_obj(service)['files']
print(f'Таблиц на диске после удаления: {len(spreadsheets)}')
