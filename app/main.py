from fastapi import FastAPI

from .routes.auth_routes import auth_router
from .routes.url_routes import url_router
from .routes.user_routes import user_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(url_router)
app.include_router(user_router)

@app.get("/")
async def root():
    print('API Funcionando')
    return { "message": "API Funcionando" }





































