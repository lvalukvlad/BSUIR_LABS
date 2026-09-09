from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import time

router = APIRouter(prefix="/upload", tags=["Загрузка файлов"])


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    Загрузка файла для анализа

    Поддерживаемые форматы: TXT, RTF
    """
    # Валидация расширения
    filename = file.filename or ""
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    allowed_extensions = ['txt', 'rtf']
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат. Разрешены: {', '.join(allowed_extensions)}"
        )

    # Чтение содержимого
    content = await file.read()

    # Проверка размера (макс 10MB)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл слишком большой (макс 10MB)")

    return {
        "success": True,
        "filename": filename,
        "size_bytes": len(content),
        "format": ext,
        "message": "Файл загружен. Используйте /api/analyze для обработки."
    }