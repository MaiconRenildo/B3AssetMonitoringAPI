from api.modules.middleware import access_token
from fastapi import APIRouter,Depends,status
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from api import app


router = APIRouter(
    tags=["b3"],
    prefix="/b3",
)




##########################################################
################################ CRIAÇÃO DA TABELA STOCKS
@app.on_event("startup")
def start_database():
    from api.modules.database import DATABASE as database
    from api.services.b3.repository import insert_assets
    from api.services.b3.model import Asset,b3_tables
    from api.services.b3.util import get_assets

    if not Asset.table_exists():
        database.create_tables(b3_tables)
        insert_assets(get_assets())
        print("Assets table created successfully")
    else:
        print("Assets table already exists")




##########################################################
#################################################### CRON 
def filter_price(array,code):
    return filter(lambda x: (x['asset_code'] == code),array)

@app.on_event("startup")
def update_cotations_history():
    from api.services.b3.util import get_asset_cotation,send_purchase_recommendation_email,send_sale_recommendation_email,is_market_closed
    from api.services.b3.repository import get_monitored_assets,insert_in_asset_monitoring_history,update_asset_monitoring_orders
    from api.modules.queue import monitoring_queue,email_queue
    from api.modules.util import now
    from datetime import timedelta

    monitoring_queue().enqueue_in(timedelta(seconds=60),update_cotations_history)

    if is_market_closed():
        print("\nThe market is closed",now(),"\n")
        return False

    monitored_assets = get_monitored_assets()

    if monitored_assets == False: 
        print("\nThere are no cotations to check -> ",now(),"\n")
        return False


    array_with_codes_and_ids_and_prices = []
    ids_and_order_types = []
    array_with_codes = []

    for i in monitored_assets:

        new_code = i['asset_code']
        new_element_with_price = {"code": i['asset_code'], "id": i['asset_id']}

        price = 0

        if new_code not in array_with_codes:
            array_with_codes.append(new_code)
            try:
                price = get_asset_cotation(new_element_with_price['code'])
                new_element_with_price['price'] = price
                array_with_codes_and_ids_and_prices.append(new_element_with_price)
            except:
                array_with_codes.remove(new_code)
        else:
            new_element_with_price['price'] = filter_price(array_with_codes_and_ids_and_prices,i['asset_code'])


        # ordem de compra
        if i['lower_price_limit'] <= price and i['upper_price_limit'] > price:
            
            if i['buy_order'] == None:
                email_queue().enqueue(
                    send_purchase_recommendation_email,
                    email=i['user_email'],
                    asset_code=i['asset_code'],
                    price=new_element_with_price['price']
                )

                ids_and_order_types.append({"id":i['monitoring_id'],"order_type": "buy"})


        # ordem de venda
        if i['upper_price_limit'] <= price:

            if i['sell_order'] == None:

                email_queue().enqueue(
                    send_sale_recommendation_email,
                    email=i['user_email'],
                    asset_code=i['asset_code'],
                    price=new_element_with_price['price']
                )

                ids_and_order_types.append({"id":i['monitoring_id'],"order_type": "sell"})
    
    update_asset_monitoring_orders(ids_and_order_types)

    if(insert_in_asset_monitoring_history(array_with_codes_and_ids_and_prices,now())):
        print("Cotations updated successfully")
        return True
    
    print("Cotations not updated")
    return False




##########################################################
##################################### COTAÇÃO DE UM ATIVO 
class CotationIn(BaseModel):
    asset_code: str = Field(...,example="CSAN3")

class CotationOut(BaseModel):
    code: str = Field(...,example="CSAN3")
    cotation: str = Field(...,example=4.10)

class CotationOut404(BaseModel):
    detail: str = Field(...,example="Code not found")

@router.get(
    path="/assets/cotation",
    description="Asset cotation route",
    responses={
        200:{"model":CotationOut},
        404:{"model":CotationOut404}
    }
)

def get_cotation(asset_code:str,user_id=Depends(access_token)):
    from api.services.b3.util import get_asset_cotation
    cotation = get_asset_cotation(asset_code)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": asset_code.upper(),
            "cotation": cotation
        }
    )




##########################################################
##################################### LISTAGEM DOS ATIVOS 
class Asset(BaseModel):
    company_name: str = Field(...,example="COSAN")
    code: str = Field(...,example="CSAN3")
    CNPJ: str = Field(...,example='50746577000115')

@router.get(
    path="/assets",
    description="List assets route",
    responses = {
        200:{"model":list[Asset]}
    }
)

def list_assets(page:int,limit:int,user_id=Depends(access_token))->list[Asset]:
    from api.services.b3.repository import get_stokes

    limit = 1 if limit<1 else limit
    page = 1 if page<1 else page

    return get_stokes(page,limit)




##########################################################
##################### HABILITA O MONITORAMENTO DE UM ATIVO 
class EnableMonitoringIn(BaseModel):
    asset_code: str = Field(...,example="CSAN3")
    upper_price_limit: float = Field(...,example=45.40)
    lower_price_limit:float = Field(...,example=10.5)


class EnableMonitoringOut(BaseModel):
    message: str = "Now the asset is being monitored"

class EnableMonitoring404(BaseModel):
    detail: str = "Code not found"

class EnableMonitoring406(BaseModel):
    detail: str = "Asset already monitored"

class EnableMonitoring422(BaseModel):
    detail: str = "Invalid limits"

@router.post(
    path="/assets/monitoring",
    description="Enable monitoring",
    responses={
        200:{"model":EnableMonitoringOut},
        404:{"model":EnableMonitoring404},
        406:{"model":EnableMonitoring406},
        422:{"model":EnableMonitoring422}
    }
)

def enable_monitoring(request:EnableMonitoringIn,user_id:int = Depends(access_token)):
    from api.services.b3.repository import insert_in_asset_monitoring,is_already_monitored,get_asset_id
    from api.modules.util import error,now

    request_data = dict(request)

    if (
        request_data["lower_price_limit"] >= request_data["upper_price_limit"] or 
        request_data["lower_price_limit"] == 0 or 
        request_data["upper_price_limit"] == 0
    ): error(422,"Invalid limits") 

    asset_id = get_asset_id(request_data['asset_code'])

    if asset_id == False : error(404,"Code not found")

    if is_already_monitored(user_id,request_data['asset_code']): error(406,"Asset already monitored")

    insert_in_asset_monitoring(
        asset_id=asset_id,
        user_id=user_id,
        upper_price_limit=request_data["upper_price_limit"],
        lower_price_limit=request_data['lower_price_limit'],
        time=now()
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message":"Now the asset is being monitored"
        }
    )




##########################################################
################## DESABILITA O MONITORAMENTO DE UM ATIVO 
class DisableMonitoringIn(BaseModel):
    asset_code: str = Field(...,example="CSAN3")

class DesableMonitoringOut(BaseModel):
    detail: str = "Now the asset is not more being monitored"

class DesableMonitoring404(BaseModel):
    detail: str = "Asset monitoring not found"

@router.delete(
    path="/assets/monitoring",
    description="Desable monitoring",
    responses={
        200:{"model":DesableMonitoringOut},
        404:{"model":DesableMonitoring404},
    }
)

def disable_monitoring(request:DisableMonitoringIn,user_id:int = Depends(access_token)):
    from api.services.b3.repository import remove_asset_monitoring
    from api.modules.util import error

    request_data = dict(request)

    is_removed = remove_asset_monitoring(user_id,request_data['asset_code'])

    if is_removed == False: error(404,"Asset monitoring not found")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message":"Now the asset is not more being monitored"
        }
    )


##########################################################
################# ATUALIZA OS PARÂMETROS DO MONITORAMENTO
class UpdateMonitoringParamsOut(BaseModel):
    message: str = "Asset monitoring params updated"

@router.put(
    path="/assets/monitoring",
    description="Update monitoring params",
    responses={
        200:{"model":UpdateMonitoringParamsOut},
        404:{"model":EnableMonitoring404},
        422:{"model":EnableMonitoring422}
    }
)

def update_monitoring_params(request:EnableMonitoringIn,user_id:int = Depends(access_token)):
    from api.services.b3.repository import update_asset_monitoring_params
    from api.modules.util import error

    request_data = dict(request)

    if (
        request_data["lower_price_limit"] >= request_data["upper_price_limit"] or 
        request_data["lower_price_limit"] == 0 or 
        request_data["upper_price_limit"] == 0
    ): error(422,"Invalid limits") 

    if update_asset_monitoring_params(
        user_id=user_id,
        asset_code=request_data['asset_code'],
        upper_price_limit=request_data['upper_price_limit'],
        lower_price_limit=request_data['lower_price_limit']
    ) == False : error(404,"Asset monitoring not found")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message":"Asset monitoring params updated"
        }
    )




##########################################################
################# BUSCA AS CONFIGURAÇÕES DE MONITORAMENTO
class GetAssetMonitoring404(BaseModel):
    message: str = "Asset monitoring not found"

class GetAssetMonitoringOut(BaseModel):
    code: str = Field(...,example="CSAN3")
    upper_price_limit: float = Field(...,example=45.40)
    lower_price_limit:float = Field(...,example=10.5)

@router.get(
    path="/assets/monitoring",
    description="Get monitoring configurations",
    responses={
        200:{"model":list[GetAssetMonitoringOut]},
        404:{"model":GetAssetMonitoring404},
    }
)

def get_monitoring_configurations(asset_code:str = None,user_id:int = Depends(access_token)):
    from api.services.b3.repository import get_assets_monitoring_by_user,get_assets_monitoring_by_user_and_asset_code
    from api.modules.util import error

    result = get_assets_monitoring_by_user(user_id) if asset_code == None else get_assets_monitoring_by_user_and_asset_code(user_id,asset_code)
    
    if result == False :
        error(404,"Asset monitoring not found")
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "assets_monitoring": result
        }
    )