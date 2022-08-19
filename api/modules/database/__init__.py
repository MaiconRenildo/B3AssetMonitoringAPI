import os
from peewee import SqliteDatabase,MySQLDatabase,Model
from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv())

SCHEMA = "INOA"

STAGE = os.getenv('STAGE')

DATABASE =  (
      SqliteDatabase(SCHEMA + '.db') if STAGE=='TEST' 
      else MySQLDatabase(SCHEMA, **
        { 
          'charset': 'utf8',
          'sql_mode': 'PIPES_AS_CONCAT',
          'use_unicode': True,
          'host': os.getenv('DB_HOST'),
          'port': int(os.getenv('DB_PORT')),
          'user': os.getenv('DB_USER'),
          'password': os.getenv('DB_PASSWORD')
        },autoconnect=True,autorollback=True
      )
    )


class DBModel(Model):
    class Meta:
        database = DATABASE


def disconnect():
    try:
        return DATABASE.close()
    except:
        ...


def connect():
    try:
        return DATABASE.connect()
    except:
        ...