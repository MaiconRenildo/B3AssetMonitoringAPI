def get_client():
    from fastapi.testclient import TestClient
    from api.main import app
    return TestClient(app)


def get_token(id):
    from api.modules.util import jwt_encode
    return jwt_encode(id)


client = get_client()