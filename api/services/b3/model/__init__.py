from peewee import AutoField, CharField,ForeignKeyField,FloatField,TimeField,BooleanField
from api.modules.database import DBModel

class Asset(DBModel):
    id = AutoField()
    code = CharField(null=False,unique=True)
    company_name = CharField(null=False,unique=False)
    CNPJ = CharField(null=False,unique=False)

    class Meta:
        table_name = 'Assets'


class AssetMonitoring(DBModel):
    from api.services.user.model import User

    id = AutoField()
    asset_id = ForeignKeyField(field='id',model=Asset)
    user_id = ForeignKeyField(field='id',model=User)
    upper_price_limit = FloatField()
    lower_price_limit = FloatField()
    created_at = TimeField()
    buy_order = BooleanField(null=True)
    sell_order = BooleanField(null=True)


class AssetMonitoringHistory(DBModel):
    id = AutoField()
    asset_id = ForeignKeyField(field='id',model=Asset)
    price = FloatField()
    time = TimeField()


b3_tables = [
    Asset,
    AssetMonitoring,
    AssetMonitoringHistory
]