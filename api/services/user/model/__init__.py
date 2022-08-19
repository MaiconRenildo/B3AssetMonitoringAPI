from peewee import AutoField, CharField
from api.modules.database import DBModel

class User(DBModel):
    id = AutoField()
    name = CharField(null=False,unique=False)
    email = CharField(null=False,unique=True)
    password = CharField(null=False,unique=False)

    class Meta:
        table_name = 'Users'


user_tables = [
    User
]