from api.services import user
from api import app

app.include_router(user.router)