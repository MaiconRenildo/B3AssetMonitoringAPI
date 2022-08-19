from test.modules.database.test_connection import create_tables,stage_test,drop_tables


def test_should_insert_assets(drop_tables,create_tables):
    from api.services.b3.repository import insert_assets
    from test.mocks import assets 

    assert insert_assets(assets.all) == True


def test_should_get_assets():
    from api.services.b3.repository import get_stokes
    assert type(get_stokes(1,1)) == list 


def test_should_get_asset_id():
    from api.services.b3.repository import get_asset_id
    assert type(get_asset_id("CSAN3")) == int
    assert get_asset_id("ANYCODE") == False


def test_should_insert_in_asset_monitoring_history():
    from api.services.b3.repository import insert_in_asset_monitoring_history
    from datetime import datetime
    import pytz

    assets = [{'id':1,'price': 50},{'id':2,'price':10.30}]

    assert insert_in_asset_monitoring_history(assets,datetime.now(tz=pytz.timezone("Brazil/East")).timestamp()) == True


def test_should_not_get_monitoring_assets():
    from api.services.b3.repository import get_monitored_assets
    assert get_monitored_assets() == False


def test_should_insert_in_asset_monitoring():
    from api.services.b3.repository import insert_in_asset_monitoring
    from api.services.user.repository import insert_user
    import time

    insert_user("maicon","maicon@gmail.com","password")

    assert insert_in_asset_monitoring(
        asset_id=1,
        user_id=1,
        upper_price_limit=10,
        lower_price_limit=5,
        time=time.time()
    ) == 1


def test_should_update_asset_monitoring_status():
    from api.services.b3.repository import update_asset_monitoring_orders,insert_in_asset_monitoring
    import time
    
    insert_in_asset_monitoring(
        asset_id=2,
        user_id=1,
        upper_price_limit=10,
        lower_price_limit=5,
        time=time.time()
    )

    assert update_asset_monitoring_orders([
        {"id":1,"order_type":"buy"},
        {"id":2,"order_type":"sell"}
    ]) == True



def test_should_get_monitoring_assets():
    from api.services.b3.repository import get_monitored_assets
    result = get_monitored_assets()[0]
    assert type(result['lower_price_limit']) == float
    assert type(result['upper_price_limit']) == float
    assert type(result['asset_code']) == str
    assert type(result['user_email']) == str
    assert type(result['asset_id']) == int
    assert type(result['user_id']) == int


def test_should_verify_if_asset_is_already_monitored():
    from api.services.b3.repository import is_already_monitored
    assert is_already_monitored(1,"CSAN3") == True
    assert is_already_monitored(2,"CSAN3") == False
    assert is_already_monitored(2,"CSAN4") == False


def test_should_update_asset_monitoring_params():
    from api.services.b3.repository import update_asset_monitoring_params
    assert update_asset_monitoring_params(user_id=1,asset_code="CSAN3",upper_price_limit=80,lower_price_limit=2) == True
    assert update_asset_monitoring_params(user_id=2,asset_code="CSAN3",upper_price_limit=80,lower_price_limit=2) == False


def test_should_get_asset_monitoring_by_user():
    from api.services.b3.repository import get_assets_monitoring_by_user
    assert get_assets_monitoring_by_user(1) == [
        {'code': 'CSAN3', 'upper_price_limit': 80.0, 'lower_price_limit': 2.0},
        {'code': 'DMMO11', 'upper_price_limit': 10.0, 'lower_price_limit': 5.0}
    ]
    assert get_assets_monitoring_by_user(2) == []


def test_should_get_asset_monitoring_by_user_and_asset_code():
    from api.services.b3.repository import get_assets_monitoring_by_user_and_asset_code
    assert get_assets_monitoring_by_user_and_asset_code(1,"CSAN3") == [{'code': 'CSAN3', 'lower_price_limit': 2.0, 'upper_price_limit': 80.0}]
    assert get_assets_monitoring_by_user_and_asset_code(2,"CSAN3") == False


def test_should_remove_asset_monitoring():
    from api.services.b3.repository import remove_asset_monitoring
    assert remove_asset_monitoring(1,"CSAN3") == 1
    assert remove_asset_monitoring(1,"CSAN3") == False