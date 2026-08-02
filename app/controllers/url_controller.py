from ..services.url_service import URLService, UniqueURLNotFoundError, MultipleURLsNotFoundError
from sqlalchemy.orm import Session
from fastapi import HTTPException

class URLController:

    @staticmethod
    def create_short_url(
        original_url: str,
        user_id: str,
        session: Session
    ):
        try:
            return URLService.create_short_url(
                original_url,
                user_id,
                session
            )
        except MultipleURLsNotFoundError as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    @staticmethod
    def access_url(
        short_code: str,
        session: Session
    ):
        try:
            return URLService.access_url(
                short_code,
                session
            )
        except UniqueURLNotFoundError as e:
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

    @staticmethod
    def list_urls(
        user_id: str,
        session: Session
    ):
        try:
            return URLService.list_urls(
                user_id,
                session
            )
        except MultipleURLsNotFoundError as e:
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

    @staticmethod
    def update_title(
        user_id: str,
        short_code: str,
        new_title: str,
        session: Session
    ):
        try:
            return URLService.update_title(
                user_id,
                short_code,
                new_title,
                session
            )
        except UniqueURLNotFoundError as e:
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

    @staticmethod
    def generate_qrcode(
        user_id: str,
        short_code: str,
        session: Session
    ):
        try:
            return URLService.generate_qrcode(
                user_id,
                short_code,
                session
            )
        except UniqueURLNotFoundError as e:
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

    @staticmethod
    def delete_url(
        user_id: str,
        short_code: str,
        session: Session
    ):
        try:
            return URLService.delete_url(
                user_id,
                short_code,
                session
            )
        except UniqueURLNotFoundError as e:
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )