from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class APIError(HTTPException):
    def __init__(
            self,
            status_code: int,
            detail: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = code or f"ERR_{status_code}"
        self.context = context or {}


class LemmaNotFoundError(APIError):
    def __init__(self, lemma: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma}' не найдена в словаре",
            code="LEMMA_NOT_FOUND",
            context={"lemma": lemma}
        )


class LemmaAlreadyExistsError(APIError):
    def __init__(self, lemma: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Лемма '{lemma}' уже существует. Используйте PUT для обновления.",
            code="LEMMA_EXISTS",
            context={"lemma": lemma}
        )


class InvalidGrammemesError(APIError):
    def __init__(self, grammemes: Dict[str, str], message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка в граммемах: {message}",
            code="INVALID_GRAMMEMES",
            context={"grammemes": grammemes}
        )


async def api_exception_handler(request: Request, exc: APIError):
    logger.warning(f"API Error: {exc.error_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": exc.error_code,
            "message": exc.detail,
            "context": exc.context,
            "path": request.url.path
        }
    )


def register_error_handlers(app):
    app.add_exception_handler(APIError, api_exception_handler)