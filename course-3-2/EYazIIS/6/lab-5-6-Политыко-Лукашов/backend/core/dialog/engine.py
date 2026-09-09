from __future__ import annotations

import time
import re
from dataclasses import dataclass, field

from core.corpus.index import search_corpus
from core.dialog import knowledge
from core.dialog.llm_fallback import ask_llm_medical, llm_enabled
from core.dialog.nlp_utils import lemmas_set, tokenize


@dataclass
class DialogTurnResult:
    reply: str
    intent: str
    processing_time_ms: int
    sources: list[dict] = field(default_factory=list)
    updated_context: dict = field(default_factory=dict)


def _has_any(lem: set[str], *words: str) -> bool:
    return any(w in lem for w in words)


def _match_specialist(lower: str) -> str | None:
    for key in sorted(knowledge.SPECIALISTS.keys(), key=len, reverse=True):
        if key in lower:
            return key
    return None


def _match_condition(lem: set[str], lower: str) -> str | None:
    for key in sorted(knowledge.CONDITIONS.keys(), key=len, reverse=True):
        if key in lower:
            return key
        parts = key.split()
        if len(parts) > 1 and all(p in lem for p in parts if len(p) > 2):
            return key
    return None


def _match_term(lower: str) -> str | None:
    for key in knowledge.TERMS:
        if key in lower:
            return key
    return None


def _symptom_bundle(lower: str) -> dict | None:
    for r in knowledge.SYMPTOM_ROUTES:
        if all(pat in lower for pat in r["patterns"]):
            return r
    return None


def _followup_more(lower: str, lem: set[str]) -> bool:
    return any(
        x in lower
        for x in (
            "подробнее",
            "подробней",
            "расскажи ещё",
            "не понял",
            "не поняла",
            "уточни",
            "уточните",
            "объясни подробнее",
        )
    ) or _has_any(lem, "уточни", "расшифруй")


def _greeting(lower: str, lem: set[str]) -> bool:
    if any(
        p in lower
        for p in (
            "здравствуй",
            "привет",
            "доброе утро",
            "добрый день",
            "добрый вечер",
            "доброй ночи",
            "доброго дня",
            "салют",
        )
    ):
        return True
    return _has_any(lem, "приветствовать", "хай")


def _goodbye(lem: set[str], lower: str) -> bool:
    if any(p in lower for p in ("до свидания", "до встречи", "увидимся", "пока-пока")):
        return True
    return _has_any(lem, "пока", "прощай")


def _help_intent(lem: set[str], text: str) -> bool:
    t = text.lower()
    return (
        _has_any(lem, "помощь", "справка", "что ты уметь", "что ты мочь", "как пользоваться")
        or "что ты" in t
        or "что вы" in t
    )


def _term_intent(lem: set[str]) -> bool:
    return _has_any(lem, "что такое", "объясни", "расшифруй") or _has_any(
        lem, "термин", "значение", "определение"
    )


def _prevention_intent(lem: set[str]) -> bool:
    return _has_any(
        lem,
        "профилактика",
        "предупредить",
        "укрепить",
        "здоровый",
        "образ жизни",
        "здоровье",
    )


def _education_query(lower: str) -> bool:
    return any(
        p in lower
        for p in (
            "что такое",
            "кто такой",
            "кто такая",
            "расскажи о ",
            "расскажи про",
            "определение",
        )
    )


def _emergency(lower: str, lem: set[str]) -> bool:
    if _education_query(lower):
        return False
    phrases = (
        "не дышать",
        "не могу дышать",
        "потеря сознания",
        "без сознания",
        "обильное кровотечение",
        "кровь хлещет",
        "вызовите скорую",
        "вызов скорой",
    )
    if any(p in lower for p in phrases):
        return True
    return _has_any(lem, "скорая", "реанимация") and _has_any(
        lem, "вызвать", "вызов", "срочно"
    )


def _extract_bp(text: str) -> tuple[int, int] | None:
    m = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", text)
    if not m:
        return None
    try:
        sys = int(m.group(1))
        dia = int(m.group(2))
    except ValueError:
        return None
    if sys < 60 or dia < 40:
        return None
    return sys, dia


def _context_patch(
    intent: str,
    cond_key: str | None,
    spec_key: str | None,
) -> dict:
    p: dict = {"last_intent": intent}
    if cond_key:
        p["last_condition"] = cond_key
    if spec_key:
        p["last_specialist"] = spec_key
    return p


def _attach_corpus(
    user_text: str,
    base_reply: str,
    min_score: float = 0.09,
) -> tuple[str, list[dict]]:
    hits = search_corpus(user_text, top_k=2, min_score=min_score)
    if not hits:
        return base_reply, []
    src = []
    blocks = []
    for h in hits:
        src.append({"score": h["score"], "meta": h["meta"], "excerpt": h["text"][:420]})
        blocks.append(h["text"][:520])
    extra = "\n\n---\n\n".join(blocks)
    reply = base_reply + "\n\nФрагменты справочного корпуса:\n" + extra
    files = sorted({h["meta"].get("file", "") for h in hits})
    reply += "\n\nФайлы: " + ", ".join(f for f in files if f)
    return reply, src


def generate_reply(
    user_text: str,
    context: dict | None = None,
    allow_llm: bool = True,
) -> DialogTurnResult:
    t0 = time.perf_counter()
    ctx = dict(context or {})
    text = (user_text or "").strip()

    def finish(
        reply: str,
        intent: str,
        *,
        cond_key: str | None = None,
        spec_key: str | None = None,
        corpus: bool = False,
    ) -> DialogTurnResult:
        sources: list[dict] = []
        if corpus:
            reply, sources = _attach_corpus(text, reply)
        ms = int((time.perf_counter() - t0) * 1000)
        return DialogTurnResult(
            reply=reply,
            intent=intent,
            processing_time_ms=ms,
            sources=sources,
            updated_context=_context_patch(intent, cond_key, spec_key),
        )

    if not text:
        ms = int((time.perf_counter() - t0) * 1000)
        return DialogTurnResult(
            "Опишите симптом или задайте вопрос по теме здоровья и медицинской информации.",
            "empty",
            ms,
            [],
            {},
        )

    lower = text.lower()
    lem = lemmas_set(text)

    lk = ctx.get("last_condition")
    if isinstance(lk, str) and lk in knowledge.CONDITIONS and _followup_more(lower, lem):
        c = knowledge.CONDITIONS[lk]
        ms = int((time.perf_counter() - t0) * 1000)
        return DialogTurnResult(
            f"{c['name']}: дополнительно — {c['note']}\n{c['summary']}",
            "followup_condition",
            ms,
            [],
            _context_patch("followup_condition", lk, None),
        )

    lspec = ctx.get("last_specialist")
    if isinstance(lspec, str) and lspec in knowledge.SPECIALISTS and _followup_more(lower, lem):
        s = knowledge.SPECIALISTS[lspec]
        ms = int((time.perf_counter() - t0) * 1000)
        return DialogTurnResult(
            f"{s['title']}: дополнительные сведения.\n{s['profile']}\nКогда обращаться: {s['when']}",
            "followup_specialist",
            ms,
            [],
            _context_patch("followup_specialist", None, lspec),
        )

    if _emergency(lower, lem):
        ms = int((time.perf_counter() - t0) * 1000)
        return DialogTurnResult(
            "При угрозе жизни, резкой боли за грудиной, нарушении дыхания, потере сознания или сильном кровотечении "
            "немедленно вызовите скорую помощь по номеру 102. "
            "Интерфейс носит справочный характер и не заменяет очный осмотр.",
            "emergency",
            ms,
            [],
            {},
        )

    bp = _extract_bp(lower)
    if bp:
        sys, dia = bp
        if sys >= 180 or dia >= 120:
            ms = int((time.perf_counter() - t0) * 1000)
            return DialogTurnResult(
                f"Давление {sys}/{dia} мм рт. ст. очень высокое и может быть опасным состоянием. "
                "Рекомендуется немедленно вызвать скорую помощь по номеру 102 и не откладывать обращение за медицинской помощью. "
                "Если есть боль в груди, выраженная одышка, сильная головная боль, слабость или нарушение речи — действуйте срочно.",
                "bp_critical",
                ms,
                [],
                {},
            )
        if sys >= 160 or dia >= 100:
            ms = int((time.perf_counter() - t0) * 1000)
            return DialogTurnResult(
                f"Давление {sys}/{dia} мм рт. ст. считается высоким и может указывать на гипертонический криз. "
                "Это состояние требует внимания, так как может приводить к серьезным осложнениям. "
                "Рекомендуется обратиться к врачу для оценки состояния и получения рекомендаций. "
                "Если появляются сильная головная боль, боль в груди, одышка или другие тревожные симптомы, срочно вызовите скорую помощь по номеру 102.",
                "bp_high",
                ms,
                [],
                {},
            )

    if _goodbye(lem, lower):
        ms = int((time.perf_counter() - t0) * 1000)
        return DialogTurnResult(
            "До свидания. История сообщений сохранена в текущей сессии.",
            "goodbye",
            ms,
            [],
            {},
        )

    if _greeting(lower, lem) and len(tokenize(text)) <= 14:
        ms = int((time.perf_counter() - t0) * 1000)
        return DialogTurnResult(
            "Здравствуйте. Система отвечает на русском языке в предметной области медицинской информации. "
            "Можно спрашивать о симптомах, специалистах, заболеваниях и терминах; часть ответов дополняется фрагментами локального текстового корпуса. "
            "Информация не является медицинским назначением.",
            "greeting",
            ms,
            [],
            {},
        )

    if _help_intent(lem, text):
        ms = int((time.perf_counter() - t0) * 1000)
        return DialogTurnResult(
            "Примеры запросов:\n"
            "• «Что такое гипертония?» / «Расскажи про ОРВИ»\n"
            "• «Когда обращаться к кардиологу?»\n"
            "• «Что такое анализ крови?»\n"
            "• «Как укрепить здоровье?»\n"
            "• Описание симптомов: «кашель и температура»\n\n"
            "Вкладка «Справка» содержит термины. Историю можно править в боковой панели. Корпус текстов лежит в каталоге data/corpus.",
            "help",
            ms,
            [],
            {},
        )

    if allow_llm and llm_enabled():
        llm_text = ask_llm_medical(text, ctx)
        if llm_text:
            ms = int((time.perf_counter() - t0) * 1000)
            return DialogTurnResult(
                llm_text,
                "llm_primary",
                ms,
                [],
                _context_patch("llm_primary", None, None),
            )

    bundle = _symptom_bundle(lower)
    if bundle:
        topic = bundle.get("topic") or ""
        ck = topic if topic in knowledge.CONDITIONS else None
        sk = topic if topic in knowledge.SPECIALISTS else None
        return finish(
            bundle["reply"],
            "symptom_bundle",
            cond_key=ck,
            spec_key=sk,
            corpus=True,
        )

    cond_key = _match_condition(lem, lower)
    if not cond_key and "простуд" in lower:
        cond_key = "орви"
    if cond_key:
        c = knowledge.CONDITIONS[cond_key]
        return finish(
            f"{c['name']}. {c['summary']}\n{c['note']}",
            "condition_info",
            cond_key=cond_key,
            corpus=True,
        )

    spec_key = _match_specialist(lower)
    if spec_key and (
        _has_any(
            lem,
            "врач",
            "специалист",
            "запись",
            "когда",
            "куда",
            "кто такой",
            "кто это",
            "направление",
        )
        or spec_key in lower
    ):
        s = knowledge.SPECIALISTS[spec_key]
        return finish(
            f"{s['title']}: {s['profile']}\nКогда обращаться: {s['when']}",
            "specialist_info",
            spec_key=spec_key,
            corpus=True,
        )

    if _term_intent(lem):
        tk = _match_term(lower)
        if tk:
            return finish(
                knowledge.TERMS[tk],
                "term",
                corpus=False,
            )
        return finish(
            "Уточните термин: например «артериальное давление», «пульс», «анализ крови», «инсулин», «ЭКГ».",
            "term_generic",
        )

    tk2 = _match_term(lower)
    if tk2:
        return finish(knowledge.TERMS[tk2], "term_short")

    if _prevention_intent(lem):
        return finish(
            "Общие рекомендации: сбалансированное питание, регулярная умеренная активность, отказ от курения, "
            "ограничение алкоголя, полноценный сон, профилактические осмотры по графику. Индивидуальный план формирует лечащий врач.",
            "prevention",
            corpus=True,
        )

    if cond_key:
        c = knowledge.CONDITIONS[cond_key]
        return finish(
            f"{c['name']}. {c['summary']}",
            "condition_inferred",
            cond_key=cond_key,
            corpus=True,
        )

    if spec_key:
        s = knowledge.SPECIALISTS[spec_key]
        return finish(
            f"{s['title']}: {s['when']}",
            "specialist_inferred",
            spec_key=spec_key,
            corpus=True,
        )

    hits = search_corpus(text, top_k=3, min_score=0.055)
    if hits:
        parts = []
        src = []
        for h in hits:
            parts.append(h["text"][:650])
            src.append({"score": h["score"], "meta": h["meta"]})
        reply = (
            "По запросу найдены наиболее близкие по смыслу фрагменты локального корпуса (лемматизация и TF–IDF):\n\n"
            + "\n\n---\n\n".join(parts)
        )
        reply += (
            "\n\nИнтерпретацию результатов и тактику лечения определяет врач после очного осмотра и обследований."
        )
        ms = int((time.perf_counter() - t0) * 1000)
        return DialogTurnResult(
            reply,
            "corpus_retrieval",
            ms,
            src,
            {},
        )

    return finish(
        "Формулировку можно уточнить: название заболевания, симптом или специальность врача из справочника. "
        "При острой угрозе жизни вызывайте скорую помощь.",
        "unknown",
        corpus=False,
    )
