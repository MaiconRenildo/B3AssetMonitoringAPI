from test.modules.database.test_connection import create_tables,stage_test,drop_tables
from test.util import client
from fastapi import status
from pytest import mark



@mark.login
def test_should_not_login(drop_tables,create_tables):

    response = client.post(url="user/login",json={
      "email":"anny@gmail.com",
      "password":"password"
    })

    assert response.json() == {'detail': 'Invalid email or password'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.login
def test_should_login():
    from api.services.user.util import encode_password
    from api.services.user.repository import insert_user

    insert_user(
      name="Anny",
      email="anny@gmail.com",
      password=encode_password("password")
    )

    response = client.post(url="user/login",json={
      "email":"anny@gmail.com",
      "password":"password"
    })

    assert type(response.json()['token']) == str
    assert response.status_code == status.HTTP_200_OK


@mark.create_user
def test_should_create_user(drop_tables,create_tables):
    
    response = client.post(url="user",json={
      "name":"Anny",
      "email":"anny@gmail.com",
      "password":"password"
    })

    assert response.json() == {'message': 'User created successfully'}
    assert response.status_code == status.HTTP_201_CREATED
   

@mark.create_user
def test_should_not_create_user_with_email_already_in_user():
    
    response = client.post(url="user",json={
      "name":"Anny",
      "email":"anny@gmail.com",
      "password":"password"
    })

    assert response.json() == {'detail': 'Email not available'}
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


@mark.create_user
def test_should_not_create_user_with_invalid_email():
    
    response = client.post(url="user",json={
      "name":"Anny",
      "email":"a@gmail.com",
      "password":"password"
    })

    assert response.json() == {'detail': 'Invalid email'}
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY