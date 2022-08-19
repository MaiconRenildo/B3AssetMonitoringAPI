from pytest import fixture

@fixture
def stage_test():
    from api.modules.database import STAGE
    assert STAGE == 'TEST'


def tables():
    from api.services.b3.model import b3_tables
    from api.services.user.model import user_tables
    return (b3_tables+user_tables)


@fixture
def create_tables(stage_test):
    from api.modules.database import DATABASE as database
    database.create_tables(models=tables())


@fixture
def drop_tables(stage_test):
    from api.modules.database import DATABASE as database
    database.drop_tables(models=tables())


def test_should_create_tables(create_tables,drop_tables):
    assert True==True