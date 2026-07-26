from fastapi import APIRouter, Depends, HTTPException
from ..schemas import URLSchema
from ..models import User, URL
from sqlalchemy.orm import Session
from ..dependencies import get_session, verify_token
from ..utils.code_generator import generate_short_code

url_router = APIRouter(prefix='/url', tags=['url'], dependencies=[Depends(verify_token)])

@url_router.get('/')
async def home():
    """
    Rota padrão de URLs
    """
    return { "message": "Home URL Route" }

@url_router.post('/create-short-url')
async def create_short_url(url_schema: URLSchema, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    """
    Rota de Encurtar URL
    """
    generated_code = generate_short_code()
    existing_codes = session.query(URL).filter(URL.short_code).all()
    short_code = ''
    # while generated_code in existing_codes:
    #     generated_code = generate_short_code()
    #     if generated_code in existing_codes:
    #         print("Código já existe")
    #     else:
    #         print("Código não existe")

    print(existing_codes)
    new_url = URL(title='', original_url=url_schema.original_url, short_code=generated_code, user_id=user.id)
    return { 
        "message": "URL Curto",
        "short-code": short_code,
        "short-url": new_url.short_url 
    }

@url_router.get('/test-code-generation')
async def test_code(session: Session = Depends(get_session)):
    generated_code = generate_short_code()

    try:
        existing_urls = session.query(URL).filter(URL.short_code == generated_code).all()
    except:
        return { "message": "Erro ao buscar URLs" }

    generated_code = generate_short_code()

    codes = []
    for url in existing_urls:
        codes.append(url.short_code)

    while generated_code in codes:
        generated_code = generate_short_code()
        if generated_code in codes:
            print("Código já existe")
        else:
            print("Código não existe")

    short_code = ''
    print(codes)
    return { 
        "message": "URL Curto",
        "short-code": short_code  
    }