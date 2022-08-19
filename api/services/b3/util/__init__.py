import os,dotenv
dotenv.load_dotenv(dotenv.find_dotenv())


def get_assets():
    import httpx
    return httpx.get(
        url="https://api-cotacao-b3.labdo.it/api/empresa",
        timeout=60
    ).json()


def get_asset_cotation(code:str):
    from api.modules.util import error
    import httpx
    response = httpx.get(
        url="https://api.hgbrasil.com/finance/stock_price?key=" + os.getenv("HG_API_KEY") + "&symbol=" + code,
        timeout=60
    ).json()['results']

    try:
        return response[code.upper()]['price']
    except:
        error(404,"Code not found")


def send_purchase_recommendation_email(asset_code:str,price:float,email:str):
    from api.modules.email import send

    return send(
        to=email,
        subject="Recomendação de compra - " + asset_code,
        msg="A cotação atual do ativo é de R$ " + str(price) + " . Conforme os parâmetros de monitoramento, sugerimos a compra." 
    )


def send_sale_recommendation_email(asset_code:str,price:float,email:str):
    from api.modules.email import send

    return send(
        to=email,
        subject="Recomendação de venda - " + asset_code,
        msg="A cotação atual do ativo é de R$ " + str(price) + " . Conforme os parâmetros de monitoramento, sugerimos a venda." 
    )


def is_market_closed():
    from datetime import datetime
    import pytz
    hour = datetime.now(tz=pytz.timezone("Brazil/East")).hour
    week_day = datetime.now(tz=pytz.timezone("Brazil/East")).weekday()

    if week_day == 5 or week_day == 6:
        return True

    return True if hour < 10 or hour>17 else False