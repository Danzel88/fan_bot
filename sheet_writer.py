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


class GoogleWriter:
    def __init__(self, sheet_name: str, values):
        self.sheet_name = sheet_name
        self.title, self.gid = self.create_new_sheet(self.sheet_name)
        self.values = values

    def formater_sheet(self):
        formater = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": self.gid,
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
                            "sheetId": self.gid,
                            "gridProperties": {
                                "frozenRowCount": 1
                            }
                        },
                        "fields": "gridProperties.frozenRowCount"
                    }
                },
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": self.gid,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 8
                        }
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=formater
        ).execute()

    def create_new_sheet(self, sheet_name: str):
        add_spsh = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        # 'title': '_'.join(sheet_name.split('_')[2:5]),
                        'title': sheet_name,
                        "gridProperties": {
                            "rowCount": 300,
                            "columnCount": 8
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
        gid = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=add_spsh
        ).execute()
        return (gid['replies'][0]['addSheet']['properties']['title'],
                gid['replies'][0]['addSheet']['properties']['sheetId'])

    def writer(self):
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [{"range": f'{self.title}!A1:H1',
                          "majorDimension": "ROWS",
                          "values": [['П/п', 'Tg_Id', 'Приветствие', 'Имя и Фамилия, Должность, проект',
                                      'Менеджер', 'Как все прошло', 'Отзыв', 'Придет ли еще']]},
                         {"range": f'{self.title}!A2:H',
                          "majorDimension": "ROWS",
                          "values": self.values}]}
        ).execute()
        self.formater_sheet()



