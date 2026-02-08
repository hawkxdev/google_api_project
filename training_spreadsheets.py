"""Авторизация и управление Google таблицами."""

import os

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


def auth() -> tuple[discovery.Resource, Credentials]:
    """Авторизация в Google API через OAuth2."""
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
    service = discovery.build('sheets', 'v4', credentials=creds)
    return service, creds


def create_spreadsheet(service: discovery.Resource) -> str:
    """Создание документа Google Sheets."""
    spreadsheet_body = {
        'properties': {
            'title': 'Бюджет путешествий',
            'locale': 'ru_RU',
        },
        'sheets': [{
            'properties': {
                'sheetType': 'GRID',
                'sheetId': 0,
                'title': 'Отпуск 2077',
                'gridProperties': {
                    'rowCount': 100,
                    'columnCount': 100,
                },
            },
        }],
    }
    request = service.spreadsheets().create(body=spreadsheet_body)
    response = request.execute()
    spreadsheet_id = response['spreadsheetId']
    print('https://docs.google.com/spreadsheets/d/' + spreadsheet_id)
    return spreadsheet_id


def set_user_permissions(spreadsheet_id: str, credentials: Credentials) -> None:
    """Выдача прав доступа к документу."""
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': 'hawkxdev@gmail.com',
    }
    drive_service = discovery.build('drive', 'v3', credentials=credentials)
    drive_service.permissions().create(
        fileId=spreadsheet_id,
        body=permissions_body,
        fields='id',
    ).execute()


service, credentials = auth()
spreadsheet_id = create_spreadsheet(service)
set_user_permissions(spreadsheet_id, credentials)
