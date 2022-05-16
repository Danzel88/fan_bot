from googleapiclient import discovery
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from config_reader import load_config

cfg = load_config('config/bot.ini')

CREDENTIAL_FILE = cfg.tg_bot.CREDENTIAL_FILE
spreadsheet_id = cfg.tg_bot.spreadsheet_id
credential = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIAL_FILE,
    ["https://www.googleapis.com/auth/drive.file",
     "https://www.googleapis.com/auth/spreadsheets"])
httpAuth = credential.authorize(httplib2.Http())
service = discovery.build("sheets", "v4", http=httpAuth)


def create_new_sheet(sheet_name: str):
    add_spsh = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': '_'.join(sheet_name.split('_')[2:5]),
                    "gridProperties": {
                        "rowCount": 300,
                        "columnCount": 7
                    },
                    'tabColor': {
                        'red': 0.44,
                        'green': 0.99,
                        'blue': 0.50
                    },
                }
            }
        }]
    }
    req = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=add_spsh
    ).execute()
    formater_sheet(req['replies'][0]['addSheet']['properties']['sheetId'])
    return req['replies'][0]['addSheet']['properties']['title']


def writer(values: list, gid_name: str):
    new_spsh = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [{"range": f'{gid_name}!A1:G1',
                      "majorDimension": "ROWS",
                      "values": [['П/п', 'Состояние', 'Где был', 'Возраст',
                                  'Город', 'Отзыв', 'Telegram ID']]},
                     {"range": f'{gid_name}!A2:G',
                      "majorDimension": "ROWS",
                      "values": values}]}
    ).execute()


def formater_sheet(sheet_id: str):
    formater = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 1.0,
                                "green": 1.0,
                                "blue": 1.0
                            },
                            "horizontalAlignment": "CENTER",
                            "textFormat": {
                                "foregroundColor": {
                                    "red": 0.0,
                                    "green": 0.0,
                                    "blue": 0.0
                                },
                                "fontSize": 12,
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {
                            "frozenRowCount": 1
                        }
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            }
        ]
    }
    req = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=formater
    ).execute()
