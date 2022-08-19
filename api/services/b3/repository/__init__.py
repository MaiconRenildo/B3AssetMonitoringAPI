from pydantic import BaseModel


class AssetWithCompanyData(BaseModel):
    company_name:str
    code: str
    CNPJ:str


class AssetMonitoringWithUserData(BaseModel):
    lower_price_limt:float
    upper_price_limt:float
    asset_code:str
    user_email:str
    asset_id:int
    user_id:int
    buy_order:bool
    sell_order:bool
    monitoring_id:int


class MonitoringParams(BaseModel):
    code:str
    upper_price_limit:float
    lower_price_limit:float



def insert_assets(assets:list)->bool:
    from api.modules.database import connect,disconnect,DATABASE as database
    from api.services.b3.model import Asset

    connect()

    with database.atomic():

      for asset in assets:

        codes = asset['cd_acao'].split(",")

        for code in codes:

          code = code.lstrip()
          
          if code != "":
            Asset.create(
              code = code,
              company_name = asset['nm_empresa'],
              CNPJ = asset['vl_cnpj']
            )

    disconnect()

    return True


def get_stokes(page:int,limit:int)->list[AssetWithCompanyData]:
    from api.modules.util import format_query_result
    from api.services.b3.model import Asset
    from api.modules import database

    database.connect()

    query = Asset.select(Asset.company_name,Asset.code,Asset.CNPJ).paginate(page,limit)
    result = format_query_result(query)

    database.disconnect()

    return result


def get_asset_id(code:str)->int|bool:
    from api.modules.util import format_query_result
    from api.services.b3.model import Asset
    from api.modules import database

    database.connect()

    query = Asset.select(Asset.id).where(Asset.code==code)
    count = query.count()

    result = format_query_result(query)[0]['id'] if count>0 else False

    database.disconnect()

    return result


def get_monitored_assets()->list[AssetMonitoringWithUserData]|bool:
    from api.modules.util import format_query_result
    from api.services.b3.model import AssetMonitoring,Asset
    from api.modules import database
    from api.services.user.model import User

    database.connect()

    query = AssetMonitoring.select(
      AssetMonitoring.lower_price_limit,
      AssetMonitoring.upper_price_limit,
      Asset.code.alias('asset_code'),
      User.email.alias("user_email"),
      AssetMonitoring.asset_id,
      AssetMonitoring.user_id,
      AssetMonitoring.buy_order,
      AssetMonitoring.sell_order,
      AssetMonitoring.id.alias("monitoring_id")
    ).join(User).join(
      Asset,on =(Asset.id==AssetMonitoring.asset_id)
    )
    
    count = query.count()

    result = format_query_result(query) if count>0 else False

    database.disconnect()

    return result


def is_already_monitored(user_id:int,code:str)->bool:
    from api.services.b3.model import AssetMonitoring,Asset
    from api.modules import database

    database.connect()

    query = AssetMonitoring.select(
      AssetMonitoring.id
    ).where(
      (AssetMonitoring.user_id==user_id) & (Asset.code==code)
    ).join(Asset)
    
    count = query.count()

    result = True if count>0 else False

    database.disconnect()

    return result


def insert_in_asset_monitoring_history(assets,time:int)->bool:
    from api.modules.database import connect,disconnect,DATABASE as database
    from api.services.b3.model import AssetMonitoringHistory

    connect()

    with database.atomic():
      for asset in assets:
        AssetMonitoringHistory.create(
          asset_id = asset['id'],
          price = asset['price'],
          time = time
        )

    disconnect()

    return True


def insert_in_asset_monitoring(
  asset_id:int,
  user_id:int,
  upper_price_limit:float,
  lower_price_limit:float,
  time:float
)->int:
    from api.modules import database
    from api.services.b3.model import AssetMonitoring

    database.connect()

    id = AssetMonitoring(
      asset_id=asset_id,
      user_id=user_id,
      upper_price_limit=upper_price_limit,
      lower_price_limit=lower_price_limit,
      created_at=time,
      status="waiting"
    ).save()

    database.disconnect()

    return id


def remove_asset_monitoring(user_id:int,asset_code:str)->int:
    from api.services.b3.model import AssetMonitoring,Asset
    from api.modules.util import format_query_result
    from api.modules import database

    database.connect()

    query = AssetMonitoring.select(AssetMonitoring.id).where((Asset.code==asset_code) & (AssetMonitoring.user_id==user_id)).join(Asset)

    if query.count() < 1:
      database.disconnect()
      return False

    id = format_query_result(query)[0]['id']

    database.disconnect()

    return AssetMonitoring.delete_by_id(id)


def update_asset_monitoring_orders(ids_and_order_types:list)->bool:
    from api.services.b3.model import AssetMonitoring
    from api.modules.database import connect,disconnect,DATABASE as database

    connect()

    with database.atomic():

      for i in ids_and_order_types:

        query = AssetMonitoring.select().where(AssetMonitoring.id==i['id'])
        
        if query.count():

          monitoring = query.get()

          if i['order_type'] == "buy":
            monitoring.buy_order = True
          else:
            monitoring.sell_order = True

          monitoring.save()

    disconnect()

    return True


def update_asset_monitoring_params(user_id:int,asset_code:str,upper_price_limit:float,lower_price_limit:float)->bool:
    from api.services.b3.model import AssetMonitoring,Asset
    from api.modules import database

    database.connect()

    query = AssetMonitoring.select().join(Asset).where((AssetMonitoring.user_id==user_id) & (Asset.code==asset_code))

    if query.count():
      monitoring = query.get()
      monitoring.upper_price_limit = upper_price_limit
      monitoring.lower_price_limit = lower_price_limit
      monitoring.sell_order = None
      monitoring.buy_order = None
      monitoring.save()

      database.disconnect()
      return True
    
    database.disconnect()
    return False


def get_assets_monitoring_by_user(user_id:int)->list[MonitoringParams]:
    from api.services.b3.model import AssetMonitoring,Asset
    from api.modules import database
    from api.modules.util import format_query_result

    database.connect()

    query = AssetMonitoring.select(Asset.code,AssetMonitoring.upper_price_limit,AssetMonitoring.lower_price_limit).join(Asset).where(AssetMonitoring.user_id==user_id)

    result = format_query_result(query) if query.count() else []

    database.disconnect()

    return result


def get_assets_monitoring_by_user_and_asset_code(user_id:int,asset_code:str)->list[MonitoringParams]|bool:
    from api.services.b3.model import AssetMonitoring,Asset
    from api.modules import database
    from api.modules.util import format_query_result

    database.connect()

    query = AssetMonitoring.select(Asset.code,AssetMonitoring.upper_price_limit,AssetMonitoring.lower_price_limit).join(Asset).where((AssetMonitoring.user_id==user_id) & (Asset.code==asset_code))

    result = format_query_result(query) if query.count() else False

    database.disconnect()

    return result