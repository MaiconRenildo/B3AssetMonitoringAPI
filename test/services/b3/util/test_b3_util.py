def test_should_get_assets():
    from api.services.b3.util import get_assets
    assert type(get_assets()) == list


def test_should_get_asset_cotation():
    from api.services.b3.util import get_asset_cotation
    assert type(get_asset_cotation("MGLU3")) == float


def test_should_not_get_asset_cotation():
    from api.services.b3.util import get_asset_cotation
    from fastapi.exceptions import HTTPException
    from fastapi import status
    try:
        get_asset_cotation("teste")
    except HTTPException as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND
        assert e.detail == "Code not found"


def test_if_market_is_closed():
        from api.services.b3.util import is_market_closed
        assert type(is_market_closed()) == bool