from googleapiclient import discovery
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from config_reader import load_config

cfg = load_config('config/bot.ini')

CREDENTIAL_FILE = cfg.tg_bot.CREDENTIAL_FILE
spreadsheet_id = cfg.tg_bot.spreadsheet_id


def writer(values: list, sheet_name: str):
    credential = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIAL_FILE,
        ["https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/spreadsheets"])
    httpAuth = credential.authorize(httplib2.Http())
    service = discovery.build("sheets", "v4", http=httpAuth)
    add_spsh = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': sheet_name,
                    "gridProperties": {
                        "rowCount": 20,
                        "columnCount": 12
                    },
                    'tabColor': {
                        'red': 0.44,
                        'green': 0.99,
                        'blue': 0.50
                    }
                }
            }
        }]
    }
    new_spsh = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
              "data": [{"range": "A1:G1",
                       "majorDimension": "ROWS",
                       "values": [['П/п', 'Состояние', 'Где был', 'Возраст',
                                   'Город', 'Отзыв', 'Telegram ID']]},
                       {"range": "A2:G",
                                "majorDimension": "ROWS",
                                "values": values}]}
                                )\
        .execute()


