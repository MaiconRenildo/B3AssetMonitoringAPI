def format_query_result(query):
    response = []
    for row in query.dicts():
        response.append(row)
    return response



def error(code:int,message:str):
    from fastapi import HTTPException
    raise HTTPException(
      status_code = code,
      detail = message,
      headers = { "X-Error" : message }
    )


def jwt_encode(user_id:int):
    import datetime,jwt,os,pytz
    from dotenv import load_dotenv,find_dotenv
    load_dotenv(find_dotenv())

    return jwt.encode(
        {
            'id': user_id,
            "exp": datetime.datetime.now(tz=pytz.timezone("Brazil/East")) + datetime.timedelta(hours=2)
        },
        os.getenv('JWT_KEY'),
        algorithm="HS256"
    )


def jwt_decode(token:str):
    import jwt,os
    from dotenv import load_dotenv,find_dotenv
    load_dotenv(find_dotenv())

    try:
        return jwt.decode(token, os.getenv('JWT_KEY'), algorithms=["HS256"])
    except:
        return False


def now():
    from datetime import datetime
    import pytz
    return datetime.now(tz=pytz.timezone("Brazil/East")).timestamp()