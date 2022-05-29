import datetime

import pandas as pd
from pandas.io.sql import DatabaseError
import shutil
import os
import sqlite3

from config.loger import loger
from sheet_writer import writer, create_new_sheet

source_db = '/home/den/code/fan_bot/databases/faneron.db'
dst_path = '/home/den/code/fan_bot/user_data_for_analize/'


def copy_db(source, dst):
    """Копируем БД"""
    try:
        shutil.copy(source, dst)
        loger.warning('Database copied successfully')
        os.path.isfile(f'{dst_path}faneron.db')
    except shutil.SameFileError:
        loger.warning("Source and destination represents the same file.")
    except PermissionError:
        loger.warning("Permission denied.")
    except FileNotFoundError:
        os.makedirs(f'{dst}')


def get_data_from_db(db_path: str, lst_id: int = None):
    """Получаем данные из БД в формате pandas DataFrame"""
    conn = sqlite3.connect(db_path)
    if lst_id:
        df = pd.read_sql(f'select * from faneron_users where id>{lst_id}', conn)
        conn.close()
    else:
        df = pd.read_sql('select * from faneron_users', conn)
        conn.close()
    return df


def df_to_excel(df):
    """Записываем DataFrame в xlsx и возвращаем имя полученного файла"""
    df.to_excel(f'{dst_path}all_users_{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx',
                index=False)
    files = sorted(os.listdir(dst_path))
    return files[-2]


def check_backup_db(db_path):
    """Проверяем наличие бэкапа БД"""
    return os.path.exists(db_path)


def write_to_google_sheet(file):
    """Запись на новый лист goolge sheet. Листу присваивается имя file
    Имя листа можно изменить в коде writer"""
    df = pd.read_excel(f'/home/den/code/fan_bot/user_data_for_analize/{file}',)
    df = df.fillna('')
    gid_name = create_new_sheet(sheet_name=file)
    writer(values=df.values.tolist(), gid_name=gid_name)


def review_processing(main_db, backup_db):
    try:
        m_db = get_data_from_db(main_db).shape[0]
        b_db = get_data_from_db(backup_db).shape[0]
        if m_db > b_db:
            write_to_google_sheet(df_to_excel(get_data_from_db(main_db, lst_id=b_db)))
            return
    except DatabaseError:
        write_to_google_sheet(df_to_excel(get_data_from_db(main_db)))
        loger.warning('First time backup db')


def main():
    if not check_backup_db(f'{dst_path}faneron.db'):
        review_processing(source_db, f'{dst_path}faneron.db')
        copy_db(source_db, f'{dst_path}faneron.db')
        return
    else:
        review_processing(source_db, f'{dst_path}faneron.db')
        copy_db(source_db, f'{dst_path}faneron.db')


if __name__ == '__main__':
    main()
