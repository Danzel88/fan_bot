import datetime
import logging
from time import sleep

import pandas as pd
import shutil
import os
import sqlite3
from sheet_writer import writer, create_new_sheet

source_db = '/home/den/code/fan_bot/databases/faneron.db'
dst_path = '/home/den/code/fan_bot/user_data_for_analize/'


formatter = '[%(asctime)s] %(levelname)8s --- %(message)s ' \
            '(%(filename)s:%(lineno)s)'
logging.basicConfig(
    filename=f'log/parser-from-'
             f'{datetime.datetime.now().strftime("%Y_%m_%d")}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING)


def copy_db(source, dst):
    try:
        shutil.copy(source, dst)
        logging.warning('Database copied successfully')
        path_db = f"{os.path.isfile(f'{dst_path}faneron.db')}"
        return path_db
    except shutil.SameFileError:
        logging.warning("Source and destination represents the same file.")
    except PermissionError:
        logging.warning("Permission denied.")
    except FileNotFoundError:
        os.makedirs(f'{dst}')


def get_data_from_db(db_path, lst_id=None):
    conn = sqlite3.connect(db_path)
    if lst_id:
        df = pd.read_sql(f'select * from faneron_users where id>{lst_id}', conn)
    else:
        df = pd.read_sql('select * from faneron_users', conn)
    return df


def db_to_excel(df):
    df.to_excel(f'{dst_path}all_users_{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx',
                index=False)
    files = os.listdir(dst_path)
    return files


def review_process(files):
    file = files[-1]
    df = pd.read_excel(f'/home/den/code/fan_bot/user_data_for_analize/{file}',)
    df = df.fillna('')
    gid_name = create_new_sheet(sheet_name=file)
    writer(values=df.values.tolist(), gid_name=gid_name)


def main():
    main_db_df = get_data_from_db('/home/den/code/fan_bot/databases/faneron.db')
    backup_db_df = get_data_from_db('/home/den/code/fan_bot/user_data_for_analize/faneron.db')
    c1 = main_db_df.shape[0]
    c2 = backup_db_df.shape[0]
    if c1 > c2:
        # try:
        df = get_data_from_db(source_db, lst_id=c2)
        files_names = db_to_excel(df)

        review_process(files_names)
        copy_db(source_db, dst_path)
        # except Exception as e:
        #     print(e)
        #     logging.error(e)
    else:
        logging.warning(f"{datetime.datetime.now().date()} Нет новых отзывов")


if __name__ == '__main__':
    main()
