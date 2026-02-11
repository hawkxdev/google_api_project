"""Бюджет путешествий — основная логика приложения."""

import argparse

from services import DRIVE_SERVICE, EMAIL_USER, SHEETS_SERVICE


def get_list_obj(service):
    response = service.files().list(
        q='mimeType="application/vnd.google-apps.spreadsheet"').execute()
    return response['files']


def clear_disk(service):
    # ЗАГЛУШКА: не удаляем реальные файлы с диска
    return 'ЗАГЛУШКА: удаление отключено (защита реальных данных)'


def set_user_permissions(service, spreadsheet_id):
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': EMAIL_USER}
    service.permissions().create(
        fileId=spreadsheet_id,
        body=permissions_body,
        fields='id'
    ).execute()


def create_spreadsheet(service, data):
    title, cash = data.split(',')
    spreadsheet_body = {
        'properties': {
            'title': title.strip(),
            'locale': 'ru_RU'
        },
        'sheets': [{
            'properties': {
                'sheetType': 'GRID',
                'sheetId': 0,
                'title': 'Отпуск',
                'gridProperties': {
                    'rowCount': 100,
                    'columnCount': 100
                }
            }
        }]
    }
    request = service.spreadsheets().create(body=spreadsheet_body)
    response = request.execute()
    spreadsheet_id = response['spreadsheetId']
    set_user_permissions(DRIVE_SERVICE, spreadsheet_id)
    spreadsheet_update_values(SHEETS_SERVICE,
                              spreadsheet_id,
                              cash,
                              default=True)
    print(f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}')
    return f'Был создан документ с ID {spreadsheet_id}'


def read_values(service, spreadsheet_id):
    range = "A1:E30"
    response = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueRenderOption='FORMULA',
    ).execute()
    return response['values']


def spreadsheet_update_values(service, spreadsheet_id, data, default=False):
    if default:
        table_values = [
            ['Бюджет путешествия'],
            ['Весь бюджет', data],
            ['Все расходы', '=SUM(E7:E30)'],
            ['Остаток', '=B2-B3'],
            ['Расходы'],
            ['Описание', 'Тип', 'Кол-во', 'Цена', 'Стоимость'],
        ]
    else:
        table_values = read_values(service, spreadsheet_id)
        table_values.append(list(map(str.strip, data.split(','))))
    request_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    request = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="A1:E30",
        valueInputOption="USER_ENTERED",
        body=request_body
    )
    request.execute()
    return 'Документ обновлён'


def main(args):
    if args.list:
        return get_list_obj(DRIVE_SERVICE)
    if args.clear_all:
        return clear_disk(DRIVE_SERVICE)
    if args.create is not None:
        return create_spreadsheet(SHEETS_SERVICE, args.create)
    spreadsheet_id = None
    if args.id is not None:
        spreadsheet_id = args.id
    else:
        spreadsheets = get_list_obj(DRIVE_SERVICE)
        if spreadsheets:
            spreadsheet_id = spreadsheets[0]['id']
    if args.update is not None:
        return spreadsheet_update_values(SHEETS_SERVICE,
                                         spreadsheet_id,
                                         args.update)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Бюджет путешествий')
    parser.add_argument('-c',
                        '--create',
                        help='Создать файл - введите "имя, бюджет"')
    parser.add_argument('-cl',
                        '--clear_all',
                        action='store_true',
                        help='Удалить все spreadsheets')
    parser.add_argument('-i', '--id', help='Указать id spreadsheet')
    parser.add_argument('-ls',
                        '--list',
                        action='store_true',
                        help='Вывести все spreadsheets')
    parser.add_argument('-u', '--update', help='Обновить данные таблицы')
    args = parser.parse_args()
    print(main(args))
