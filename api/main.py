from api.services import user,b3
from api import app

app.include_router(user.router)
app.include_router(b3.router)