from fastapi import APIRouter, Depends, HTTPException
from ..schemas import URLSchema
from ..models import User, URL
from sqlalchemy.orm import Session
from ..dependencies import get_session, verify_token
from ..utils.code_generator import generate_short_code
from ..config import settings
import qrcode
from io import BytesIO
import base64
from fastapi.responses import StreamingResponse

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

@url_router.get('/generate-qrcode/{short_code}')
async def generate_qrcode(short_code: str, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    """
    Rota de Geração de QR Code para a URL Encurtada
    """
    try:
        url = session.query(URL).filter(URL.short_code == short_code, URL.user_id == user.id).first()
    except:
        return { "message": "Erro ao buscar URL" }

    if not url:
        raise HTTPException(status_code=404, detail="URL não encontrada")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f'{url.original_url}')
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return { 
        "message": "QR Code gerado com sucesso",
        "short-code": url.short_code,
        "qrcode": img_str
    }
    # return StreamingResponse(
    #     buffered,
    #     media_type="image/png"
    # )


@url_router.delete('/delete-url/{short_code}')
async def delete_url(short_code: str, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    """
    Rota de Exclusão da URL Encurtada
    """
    try:
        url = session.query(URL).filter(URL.short_code == short_code, URL.user_id == user.id).first()
    except:
        return { "message": "Erro ao buscar URL" }

    if not url:
        raise HTTPException(status_code=404, detail="URL não encontrada")

    session.delete(url)
    session.commit()

    return { 
        "message": "URL excluída com sucesso",
        "short-code": short_code
    }