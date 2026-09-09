import os

import httpx


def llm_enabled() -> bool:
    return True


def _base_url() -> str:
    return os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")


def _model() -> str:
    return os.getenv("LLM_MODEL", "openai/gpt-4o-mini")


def _timeout_s() -> float:
    try:
        return float(os.getenv("LLM_TIMEOUT_SECONDS", "12"))
    except ValueError:
        return 12.0


def ask_llm_medical(
    query: str,
    context: dict | None = None,
) -> str | None:
    key = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not key:
        return None

    ctx = context or {}
    last_condition = ctx.get("last_condition")
    last_specialist = ctx.get("last_specialist")

    sys_prompt = (
        "Ты медицинский информационный ассистент. "
        "Отвечай только на русском, кратко и по делу. "
        "Не ставь диагноз и не назначай лечение. "
        "Если есть признаки угрозы жизни, явно советуй срочно вызвать скорую помощь по номеру 102. "
        "Если вопрос не медицинский — вежливо скажи, что поддерживается медицинская тематика."
    )
    user_prompt = (
        f"Вопрос пользователя: {query}\n"
        f"Контекст: last_condition={last_condition}, last_specialist={last_specialist}\n"
        "Дай структурированный ответ в 3-6 предложениях."
    )

    payload = {
        "model": _model(),
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 380,
    }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=_timeout_s()) as client:
            resp = client.post(
                f"{_base_url()}/chat/completions",
                json=payload,
                headers=headers,
            )
            if resp.status_code >= 300:
                return None
            data = resp.json()
    except Exception:
        return None

    try:
        text = data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None

    if not text:
        return None
    return text
