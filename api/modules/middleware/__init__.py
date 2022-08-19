from fastapi import Depends,HTTPException
from fastapi.security import HTTPBearer
from api.modules.util import jwt_decode


def access_token(authorization: str = Depends(HTTPBearer())):
    authorization = dict(authorization)
    credential = authorization['credentials']
    jwt_decoded = jwt_decode(credential)

    if(jwt_decoded and jwt_decoded.get('id',False) and jwt_decoded.get('exp',False)):
        return jwt_decoded.get('id')
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )