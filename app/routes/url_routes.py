from fastapi import APIRouter, Depends, HTTPException
from ..schemas import URLSchema, UpdateTitleSchema
from ..models import User, URL
from sqlalchemy.orm import Session
from ..dependencies import get_session, verify_token
from ..utils.code_generator import generate_short_code
from ..config import settings
import qrcode
from io import BytesIO
import base64
from fastapi.responses import StreamingResponse
from ..controllers.url_controller import URLController 

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

    url = URLController.create_short_url(
        original_url = url_schema.original_url,
        user_id = user.id,
        session = session
    )

    return { 
        "message": "URL Curto",
        "short-code": url.short_code,
        "short-url": f'{settings.API_URL}/{url.short_code}'
    }

@url_router.get('/access-url/{short_code}')
async def access_url(short_code: str, session: Session = Depends(get_session)):
    """
    Rota de Acesso a URL Encurtada
    """
    url = URLController.access_url(
        short_code = short_code,
        session = session
    )

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

    url_list = URLController.list_urls(
        user_id = user.id,
        session = session
    )

    return { 
        "message": "URLs do Usuário",
        "urls": url_list
    }

@url_router.patch('/update-title/{short_code}')
async def update_title(short_code: str, title_schema: UpdateTitleSchema, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    """
    Rota de Atualização do Título da URL Encurtada
    """

    title = URLController.update_title(
        user_id = user.id,
        short_code = short_code,
        new_title = title_schema.title,
        session = session
    )

    return { 
        "message": "Título atualizado com sucesso",
        "new-title": title
    }

@url_router.get('/generate-qrcode/{short_code}')
async def generate_qrcode(short_code: str, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    """
    Rota de Geração de QR Code para a URL Encurtada
    """

    img_str = URLController.generate_qrcode(
        user_id = user.id,
        short_code = short_code,
        session = session
    )

    return { 
        "message": "QR Code gerado com sucesso",
        "qrcode": img_str
    }

@url_router.delete('/delete-url/{short_code}')
async def delete_url(short_code: str, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    """
    Rota de Exclusão da URL Encurtada
    """

    short_code = URLController.delete_url(
        user_id = user.id,
        short_code = short_code,
        session = session
    )

    return { 
        "message": "URL excluída com sucesso",
        "short-code": short_code
    }