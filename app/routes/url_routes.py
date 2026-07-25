from fastapi import APIRouter

url_router = APIRouter(prefix='/url', tags=['url'])

@url_router.get('/')
async def home():
    """
    Rota padrão de URLs
    """
    return { "message": "Home URL Route" }
