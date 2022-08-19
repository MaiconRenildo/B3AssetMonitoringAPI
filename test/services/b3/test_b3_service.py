from test.modules.database.test_connection import create_tables,stage_test,drop_tables
from test.util import client
from fastapi import status
from pytest import mark


@mark.get_cotation
def test_should_not_get_cotation_without_auth(drop_tables,create_tables):
    response = client.get(url="b3/assets/cotation?asset_code=CSAN3")
    assert response.json() == {'detail': 'Not authenticated'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


@mark.get_cotation
def test_should_not_get_cotation_with_invalid_auth():
    response = client.get(url="b3/assets/cotation?asset_code=CSAN3",headers={
      "Authorization": "Bearer " + "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjYwNTgwODUzfQ.15K3Jggofpitjm3huksKlRE6Jmt-37WCi2GSmdXlkVA"
    })
    assert response.json() == {'detail': 'Invalid token'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.get_cotation
def test_should_not_get_cotation_with_invalid_code():
    from api.modules.util import jwt_encode

    response = client.get(url="b3/assets/cotation?asset_code=C",headers={
      "Authorization": "Bearer " + jwt_encode(1)
    })

    assert response.json() == {'detail': 'Code not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


@mark.get_cotation
def test_should_get_cotation():
    from api.modules.util import jwt_encode

    response = client.get(url="b3/assets/cotation?asset_code=CSAN3",headers={
      "Authorization": "Bearer " + jwt_encode(1)
    })

    response.json()['code'] == 'CSAN3'
    response.json()['cotation'] > 0
    assert response.status_code == status.HTTP_200_OK


@mark.list_assets
def test_should_not_list_assets_without_auth(drop_tables,create_tables):
    response = client.get(url="b3/assets?page=1&limit=1")
    assert response.json() == {'detail': 'Not authenticated'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


@mark.list_assets
def test_should_not_list_assets_without_invalid_auth():
    response = client.get(url="b3/assets?page=1&limit=1",headers={
      "Authorization": "Bearer " + "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjYwNTgwODUzfQ.15K3Jggofpitjm3huksKlRE6Jmt-37WCi2GSmdXlkVA"
    })
    assert response.json() == {'detail': 'Invalid token'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.list_assets
def test_should_list_assets():
    from api.services.b3.repository import insert_assets
    from api.modules.util import jwt_encode
    from test.mocks import assets

    insert_assets(assets.all)
    
    response = client.get(url="b3/assets?page=1&limit=1",headers={
       "Authorization": "Bearer " + jwt_encode(1)
    })

    assert response.json() == [{'CNPJ': '50746577000115', 'code': 'CSAN3', 'company_name': 'COSAN'}]
    assert response.status_code == status.HTTP_200_OK



@mark.enable_monitoring
def test_should_not_enable_monitoring_without_auth(drop_tables,create_tables):
    from api.services.b3.repository import insert_assets
    from test.mocks import assets

    insert_assets(assets.all)

    response = client.post(url="b3/assets/monitoring")
    assert response.json() == {'detail': 'Not authenticated'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


@mark.enable_monitoring
def test_should_not_enable_monitoring_with_invalid_auth():
    response = client.post(url="b3/assets/monitoring",headers={
      "Authorization": "Bearer " + "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjYwNTgwODUzfQ.15K3Jggofpitjm3huksKlRE6Jmt-37WCi2GSmdXlkVA"
    })
    assert response.json() == {'detail': 'Invalid token'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.enable_monitoring
def test_should_not_enable_monitoring_with_invalid_code():
    from api.modules.util import jwt_encode

    response = client.post(url="b3/assets/monitoring",json={
      "asset_code": "gol",
      "upper_price_limit": 10,
      "lower_price_limit":4
    },headers={
             "Authorization": "Bearer " + jwt_encode(1)
    })
    
    assert response.json() == {'detail': 'Code not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


@mark.enable_monitoring
def test_should_not_enable_monitoring_with_invalid_limits():
    from api.modules.util import jwt_encode

    response = client.post(url="b3/assets/monitoring",json={
      "asset_code": "CSAN3",
      "upper_price_limit": 10,
      "lower_price_limit":11
    },headers={
             "Authorization": "Bearer " + jwt_encode(1)
    })
    
    assert response.json() == {'detail': 'Invalid limits'}
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@mark.enable_monitoring
def test_should_not_enable_monitoring_with_zero_in_one_limit():
    from api.modules.util import jwt_encode

    response = client.post(url="b3/assets/monitoring",json={
      "asset_code": "CSAN3",
      "upper_price_limit": 10,
      "lower_price_limit":0
    },headers={
             "Authorization": "Bearer " + jwt_encode(1)
    })
    
    assert response.json() == {'detail': 'Invalid limits'}
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@mark.enable_monitoring
def test_should_enable_monitoring():
    from api.modules.util import jwt_encode

    response = client.post(url="b3/assets/monitoring",json={
      "asset_code": "CSAN3",
      "upper_price_limit": 10,
      "lower_price_limit":5
    },headers={
             "Authorization": "Bearer " + jwt_encode(1)
    })
    
    assert response.json() == {'message': 'Now the asset is being monitored'}
    assert response.status_code == status.HTTP_200_OK


@mark.enable_monitoring
def test_should_enable_monitoring_if_asset_already_monitored():
    from api.modules.util import jwt_encode

    response = client.post(url="b3/assets/monitoring",json={
      "asset_code": "CSAN3",
      "upper_price_limit": 10,
      "lower_price_limit":5
    },headers={
             "Authorization": "Bearer " + jwt_encode(1)
    })
    
    assert response.json() == {'detail': 'Asset already monitored'} 
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


@mark.disable_monitoring
def test_should_disable_monitoring_without_auth(drop_tables,create_tables):
    response = client.delete(url="b3/assets/monitoring")
    assert response.json() == {'detail': 'Not authenticated'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


@mark.disable_monitoring
def test_should_disable_monitoring_with_invalid_auth():
    response = client.delete(url="b3/assets/monitoring",headers={
      "Authorization": "Bearer " + "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjYwNTgwODUzfQ.15K3Jggofpitjm3huksKlRE6Jmt-37WCi2GSmdXlkVA"
    })
    assert response.json() == {'detail': 'Invalid token'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.disable_monitoring
def test_should_not_disable_monitoring_if_asset_is_not_monitored():
    from api.services.b3.repository import insert_in_asset_monitoring,insert_assets
    from api.modules.util import jwt_encode
    from test.mocks import assets
    from time import time

    insert_assets(assets.all)
    insert_in_asset_monitoring(
      asset_id=1,
      user_id=1,
      upper_price_limit=10,
      lower_price_limit=2,
      time=time()
    )

    response = client.delete(url="b3/assets/monitoring",json={
      "asset_code": "CSAN4",
    },headers={
             "Authorization": "Bearer " + jwt_encode(1)
    })
    
    assert response.json() == {'detail': 'Asset monitoring not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


@mark.disable_monitoring
def test_should_disable_monitoring():
    from api.modules.util import jwt_encode

    response = client.delete(url="b3/assets/monitoring",json={
      "asset_code": "CSAN3",
    },headers={
             "Authorization": "Bearer " + jwt_encode(1)
    })
    
    assert response.json() == {'message': 'Now the asset is not more being monitored'}
    assert response.status_code == status.HTTP_200_OK


@mark.update_monitoring_params
def test_should_not_update_monitoring_params_without_auth(drop_tables,create_tables):
    response = client.put(url="b3/assets/monitoring")
    assert response.json() == {'detail': 'Not authenticated'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


@mark.update_monitoring_params
def test_should_not_update_monitoring_params_with_invalid_auth():
    response = client.put(url="b3/assets/monitoring",headers={
      "Authorization": "Bearer " + "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjYwNTgwODUzfQ.15K3Jggofpitjm3huksKlRE6Jmt-37WCi2GSmdXlkVA"
    })
    assert response.json() == {'detail': 'Invalid token'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.update_monitoring_params
def test_should_not_update_monitoring_params_if_monitoring_not_exists():
    from api.modules.util import jwt_encode

    response = client.put(url="b3/assets/monitoring",json={
      "asset_code": "CSAN3",
      "upper_price_limit": 10,
      "lower_price_limit":5
    },headers={
      "Authorization": "Bearer " + jwt_encode(1)
    })

    assert response.json() == {'detail': 'Asset monitoring not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


@mark.update_monitoring_params
def test_should_update_monitoring_params():
    from api.services.b3.repository import insert_in_asset_monitoring,insert_assets
    from api.modules.util import jwt_encode
    from test.mocks import assets
    from time import time

    insert_assets(assets.all)
    insert_in_asset_monitoring(
      asset_id=1,
      user_id=1,
      upper_price_limit=10,
      lower_price_limit=2,
      time=time()
    )

    response = client.put(url="b3/assets/monitoring",json={
      "asset_code": "CSAN3",
      "upper_price_limit": 10,
      "lower_price_limit":5
    },headers={
      "Authorization": "Bearer " + jwt_encode(1)
    })

    assert response.json() == {'message': 'Asset monitoring params updated'}
    assert response.status_code == status.HTTP_200_OK



@mark.get_monitoring_configurations
def test_should_not_get_monitoring_configurations_without_auth(drop_tables,create_tables):
    response = client.get(url="b3/assets/monitoring")
    assert response.json() == {'detail': 'Not authenticated'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


@mark.get_monitoring_configurations
def test_should_not_get_monitoring_configurations_with_invalid_auth():
    response = client.get(url="b3/assets/monitoring",headers={
      "Authorization": "Bearer " + "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjYwNTgwODUzfQ.15K3Jggofpitjm3huksKlRE6Jmt-37WCi2GSmdXlkVA"
    })
    assert response.json() == {'detail': 'Invalid token'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.get_monitoring_configurations
def test_should_not_get_monitoring_configurations_by_asset_code():
    from api.modules.util import jwt_encode
    response = client.get(url="b3/assets/monitoring?asset_code=CSAN3",headers={
      "Authorization": "Bearer " + jwt_encode(1)
    })
    assert response.json() == {'detail': 'Asset monitoring not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


@mark.get_monitoring_configurations
def test_should_not_get_monitoring_configurations():
    from api.modules.util import jwt_encode
    response = client.get(url="b3/assets/monitoring",headers={
      "Authorization": "Bearer " + jwt_encode(1)
    })
    assert response.json() == {'assets_monitoring': []}
    assert response.status_code == status.HTTP_200_OK


@mark.get_monitoring_configurations
def test_should_get_monitoring_configurations_by_asset_code():
    from api.services.b3.repository import insert_in_asset_monitoring,insert_assets
    from api.modules.util import jwt_encode
    from test.mocks import assets
    from time import time

    insert_assets(assets.all)
    insert_in_asset_monitoring(
      asset_id=1,
      user_id=1,
      upper_price_limit=10,
      lower_price_limit=2,
      time=time()
    )

    response = client.get(url="b3/assets/monitoring?asset_code=CSAN3",headers={
      "Authorization": "Bearer " + jwt_encode(1)
    })

    assert response.json() == {'assets_monitoring': [{'code': 'CSAN3', 'upper_price_limit': 10.0, 'lower_price_limit': 2.0}]}
    assert response.status_code == status.HTTP_200_OK


@mark.get_monitoring_configurations
def test_should_get_monitoring_configurations():
    from api.modules.util import jwt_encode

    response = client.get(url="b3/assets/monitoring",headers={
      "Authorization": "Bearer " + jwt_encode(1)
    })

    assert response.json() == {'assets_monitoring': [{'code': 'CSAN3', 'upper_price_limit': 10.0, 'lower_price_limit': 2.0}]}
    assert response.status_code == status.HTTP_200_OK