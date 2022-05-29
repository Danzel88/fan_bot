import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str
    admin_id: int
    db_name: str
    db_path: str
    CREDENTIAL_FILE: str
    spreadsheet_id: str
    mailing_db_path: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(tg_bot=TgBot(token=tg_bot['token'],
                               admin_id=int(tg_bot['admin_id']),
                               db_path=tg_bot['db_path'],
                               db_name=tg_bot['db_name'],
                               CREDENTIAL_FILE=tg_bot['CREDENTIAL_FILE'],
                               spreadsheet_id=tg_bot['spreadsheet_id'],
                               mailing_db_path=tg_bot['mailing_db_path']))
