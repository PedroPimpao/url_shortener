from fastapi import FastAPI

from .routes.auth_routes import auth_router
from .routes.url_routes import url_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(url_router)

@app.get("/")
async def root():
    print('API Funcionando')
    return { "message": "API Funcionando" }





































