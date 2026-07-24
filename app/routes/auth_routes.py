from fastapi import APIRouter, Depends, HTTPException

auth_router = APIRouter(prefix='/auth', tags=['auth'])

@auth_router.get('/')
async def home():
    """
    Rota padrão de autenticação
    """
    return { "message": "Home Auth Route" }

