import pandas as pd
import datetime
from database import database as db


def user_unload():
    file = db.unload()
    print(file)
