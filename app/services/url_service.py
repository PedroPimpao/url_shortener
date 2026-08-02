from sqlalchemy.orm import Session
from ..models import URL
from ..utils.code_generator import generate_short_code
import qrcode
from io import BytesIO
import base64

class UniqueURLNotFoundError(Exception):
    pass

class MultipleURLsNotFoundError(Exception):
    pass

class URLService:
    @staticmethod
    def create_short_url(original_url: str, user_id: str, session: Session):
        generated_code = generate_short_code()
        
        try:
            existing_urls = session.query(URL).all()
        except:
            raise MultipleURLsNotFoundError('Erro ao buscar URLs')
    
        codes = []
        for url in existing_urls:
            codes.append(url.short_code)
    
        while generated_code in codes:
            generated_code = generate_short_code()
            if generated_code in codes:
                generated_code = generate_short_code()
    
        new_url = URL(title='', original_url=original_url, short_code=generated_code, user_id=user_id)
        session.add(new_url)
        session.commit()
        return new_url

    @staticmethod
    def access_url(short_code: str, session: Session):
        try:
            url = session.query(URL).filter(URL.short_code == short_code).first()
        except:
            raise UniqueURLNotFoundError('Erro ao buscar URL') 
    
        if not url:
            raise UniqueURLNotFoundError('URL não encontrada')
    
        url.clicks += 1
        session.commit()
        return url

    @staticmethod
    def list_urls(user_id: str, session: Session):
        try:
            urls = session.query(URL).filter(URL.user_id == user_id).all()
        except:
            raise MultipleURLsNotFoundError('Erro ao buscar URLs')
    
        if not urls:
            raise MultipleURLsNotFoundError('Nenhuma URL encontrada para o usuário')
    
        url_list = []
        for url in urls:
            url_list.append({
                "original-url": url.original_url,
                "short-code": url.short_code,
                "clicks": url.clicks
               })

        return url_list

    @staticmethod
    def update_title(user_id: str, short_code: str, new_title: str, session: Session):
        try:
            url = session.query(URL).filter(URL.short_code == short_code, URL.user_id == user_id).first()
        except:
            raise UniqueURLNotFoundError("Erro ao buscar URL")
    
        if not url:
            raise UniqueURLNotFoundError("URL não encontrada")
    
        url.title = new_title
        session.commit()

        return url.title

    @staticmethod
    def generate_qrcode(user_id: str, short_code: str, session: Session):
        try:
            url = session.query(URL).filter(URL.short_code == short_code, URL.user_id == user_id).first()
        except:
            raise UniqueURLNotFoundError("Erro ao buscar URL")
    
        if not url:
            raise UniqueURLNotFoundError("Erro ao buscar URL")
    
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

        return img_str

    @staticmethod
    def delete_url(user_id: str, short_code: str, session: Session):
        try:
            url = session.query(URL).filter(URL.short_code == short_code, URL.user_id == user_id).first()
        except:
            raise UniqueURLNotFoundError("Erro ao buscar URL")
    
        if not url:
            raise UniqueURLNotFoundError("Erro ao buscar URL")
    
        session.delete(url)
        session.commit()

        return short_code