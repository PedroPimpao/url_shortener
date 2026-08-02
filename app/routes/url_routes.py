from fastapi import APIRouter, Depends, HTTPException
from ..schemas import URLSchema
from ..models import User, URL
from sqlalchemy.orm import Session
from ..dependencies import get_session, verify_token
from ..utils.code_generator import generate_short_code
from ..config import settings

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

    try:
        existing_urls = session.query(URL).all()
    except:
        return { "message": "Erro ao buscar URLs" }

    codes = []
    for url in existing_urls:
        codes.append(url.short_code)

    while generated_code in codes:
        generated_code = generate_short_code()
        if generated_code in codes:
            generated_code = generate_short_code()

    new_url = URL(title='', original_url=url_schema.original_url, short_code=generated_code, user_id=user.id)
    session.add(new_url)
    session.commit()
    return { 
        "message": "URL Curto",
        "short-code": new_url.short_code,
        "short-url": f'{settings.API_URL}/{new_url.short_code}'
    }

@url_router.get('/access-url/{short_code}')
async def access_url(short_code: str, session: Session = Depends(get_session)):
    """
    Rota de Acesso a URL Encurtada
    """
    try:
        url = session.query(URL).filter(URL.short_code == short_code).first()
    except:
        return { "message": "Erro ao buscar URL" }

    if not url:
        raise HTTPException(status_code=404, detail="URL não encontrada")

    url.clicks += 1
    session.commit()

    return { 
        "message": "URL Original",
        "original-url": url.original_url,
        "clicks": url.clicks
    }

@url_router.get('/list_urls')
async def list_urls(session: Session = Depends(get_session), user: User = Depends(verify_token)):
    """
    Rota de Listagem de URLs do Usuário
    """
    try:
        urls = session.query(URL).filter(URL.user_id == user.id).all()
    except:
        return { "message": "Erro ao buscar URLs" }

    if not urls:
        return { "message": "Nenhuma URL encontrada" }

    url_list = []
    for url in urls:
        url_list.append({
            "original-url": url.original_url,
            "short-code": url.short_code,
            "clicks": url.clicks
        })

    return { 
        "message": "URLs do Usuário",
        "urls": url_list
    }

@url_router.patch('/update-title/{short_code}')
async def update_title(short_code: str, title: str, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    """
    Rota de Atualização do Título da URL Encurtada
    """
    try:
        url = session.query(URL).filter(URL.short_code == short_code, URL.user_id == user.id).first()
    except:
        return { "message": "Erro ao buscar URL" }

    if not url:
        raise HTTPException(status_code=404, detail="URL não encontrada")

    url.title = title
    session.commit()

    return { 
        "message": "Título atualizado com sucesso",
        "short-code": url.short_code,
        "new-title": url.title
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