from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.auth_routes import auth_router
from .routes.url_routes import url_router
from .routes.user_routes import user_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(url_router)
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/")
async def root():
    print('API Funcionando')
    return { "message": "API Funcionando" }





































