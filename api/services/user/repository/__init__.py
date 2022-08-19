def insert_user(name:str,email:str,password:str)->int:
    from api.services.user.model import User
    from api.modules import database

    database.connect()

    user = User(
      password=password,
      email=email,
      name=name,
    ).save()

    database.disconnect()

    return user


def find_user_by_login_data(email:str,password:str)->int|bool:
    from api.modules.util import format_query_result
    from api.services.user.model import User
    from api.modules import database

    database.connect()

    query =  User.select(User.id).where(
        ( (User.password == password) & (User.email == email) )
    )

    count = query.count()

    database.disconnect()

    return False if count < 1 else format_query_result(query)[0]['id']


def is_email_available(email:str)->int|bool:
    from api.services.user.model import User
    from api.modules import database

    database.connect()

    query =  User.select(User.id).where(User.email == email)

    count = query.count()

    database.disconnect()

    return True if count < 1 else False