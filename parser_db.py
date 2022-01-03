import datetime
import logging

import pandas as pd
import shutil
import os
import sqlite3


source_db = '/home/den/code/fan_bot/faneron_users.db'
# source_db = '/home/den/faneron_users.db'
dst_path = '/home/den/code/fan_bot/user_data_for_analize/'


formatter = '[%(asctime)s] %(levelname)8s --- %(message)s ' \
            '(%(filename)s:%(lineno)s)'
logging.basicConfig(
    filename=f'code/fan_bot/log/parser-from-'
             f'{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING)


def copy_db(source, dst):
    try:
        shutil.copy(source, dst)
        logging.warning('Database copied successfully')
        path_db = f"{os.path.isfile(f'{dst_path}faneron_users.db')}"
        return path_db
    except shutil.SameFileError:
        logging.warning("Source and destination represents the same file.")
    except PermissionError:
        logging.warning("Permission denied.")
    except FileNotFoundError:
        os.makedirs(f'{dst}')


def db_to_excel(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql('select * from faneron_users', conn)
    df.to_excel(f'{dst_path}all_users_'
                f'{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.xlsx',
                index=False)


def main():
    res = copy_db(source_db, dst_path)
    logging.warning(res)
    if res:
        logging.warning('copeid')
        db_to_excel(f"{dst_path}faneron_users.db")
    else:
        logging.warning("source for parse not found")


if __name__ == '__main__':
    main()
