from test.modules.database.test_connection import create_tables,stage_test,drop_tables


def test_should_insert_user(drop_tables,create_tables):
    from api.services.user.repository import insert_user
    assert insert_user(name="Maicon",email="maicon@gmail.com",password="PASSWORD") == 1


def test_should_find_user_by_login_data():
    from api.services.user.repository import find_user_by_login_data
    assert find_user_by_login_data(email="maicon@gmail.com",password="PASSWORD") == 1
    assert find_user_by_login_data(email="any@gmail.com",password="pass") == False


def test_should_verify_if_is_email_available():
    from api.services.user.repository import is_email_available
    assert is_email_available("maicon@gmail.com") == False
    assert is_email_available("any@gmail.com") == True