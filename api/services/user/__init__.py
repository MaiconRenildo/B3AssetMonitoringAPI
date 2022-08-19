
from fastapi.responses import JSONResponse
from fastapi import APIRouter,status
from pydantic import BaseModel,Field
from api import app


router = APIRouter(
    tags=["user"],
    prefix="/user",
)




##########################################################
################################# CRIAÇÃO DA TABELA USERS
@app.on_event("startup")
def start_database():
    from api.modules.database import DATABASE as database
    from api.services.user.model import User,user_tables

    if not User.table_exists():
        database.create_tables(user_tables)
        print("Users table created successfully")
    else:
        print("User table already exists")




##########################################################
###################################### CRIAÇÃO DE USUÁRIO 
class UserIn(BaseModel):
    name: str = Field(...,min_length=3,example="Anny")
    email: str = Field(...,example="anny@gmail.com")
    password: str = Field(...,example="Password")

class UserOut(BaseModel):
    message: str = "User created successfully"

class InvalidEmail(BaseModel):
    detail: str = "Invalid email"

class EmailNotAvailable(BaseModel):
    detail: str = "Email not available"

@router.post(
    path="",
    description="User creation route",
    status_code=status.HTTP_201_CREATED,
    responses={
        201:{"model":UserOut},
        422:{"model":InvalidEmail},
        406:{"model":EmailNotAvailable}
    },
    
)

def create_user(request:UserIn):
    from api.services.user.repository import insert_user,is_email_available
    from api.services.user.util import encode_password
    from api.modules.util import error
    from api.modules import email
    
    user_data = dict(request)

    if email.is_valid(user_data['email']) == False : error(422,"Invalid email")

    if is_email_available(user_data["email"]) == False : error(406,"Email not available")

    insert_user(
        password=encode_password(user_data['password']),
        email=user_data["email"],
        name=user_data['name'],
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "User created successfully"
        }
    )




##########################################################
################################################### LOGIN 
class LoginIn(BaseModel):
    email: str = Field(...,example="anny@gmail.com")
    password: str = Field(...,min_length=8,example="Password")

class LoginOut(BaseModel):
    token: str = Field(...,
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjYwNTgwODUzfQ.15K3Jggofpitjm3huksKlRE6Jmt-37WCi2GSmdXlkVA"
    )

class InvalidEmailOrPassword(BaseModel):
    detail: str = "Invalid email or password"

@router.post(
    path="/login",
    description="Login route",
    responses={
        200:{"model": LoginOut},
        401:{"model": InvalidEmailOrPassword}
    }
)

def login(request:LoginIn):
    from api.services.user.repository import find_user_by_login_data
    from api.services.user.util import encode_password
    from api.modules.util import error,jwt_encode
    
    login_data = dict(request)

    user_id = find_user_by_login_data(
        password=encode_password(login_data['password']),
        email=login_data['email']
    )
    
    if user_id == False : error(401,"Invalid email or password")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "token": jwt_encode(user_id)
        }
    )