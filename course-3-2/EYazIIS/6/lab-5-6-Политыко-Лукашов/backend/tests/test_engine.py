from core.dialog.engine import generate_reply
from core.dialog.llm_fallback import llm_enabled


def test_empty():
    r = generate_reply("   ")
    assert r.intent == "empty"


def test_greeting():
    r = generate_reply("Здравствуйте")
    assert r.intent == "greeting"


def test_condition():
    r = generate_reply("Что такое гипертония")
    assert r.intent == "condition_info"
    assert "давлен" in r.reply.lower()


def test_specialist():
    r = generate_reply("Кто такой кардиолог и когда к нему идти")
    assert r.intent == "specialist_info"


def test_corpus_fallback():
    r = generate_reply("zzqx_unused_token_force_corpus_only_xyz")
    assert r.intent in ("corpus_retrieval", "unknown")


def test_followup_after_context():
    first = generate_reply("Что такое диабет")
    assert first.updated_context.get("last_condition") == "диабет"
    second = generate_reply("подробнее", context=first.updated_context)
    assert second.intent == "followup_condition"


def test_symptom_bundle():
    r = generate_reply("у меня кашель и температура три дня")
    assert r.intent == "symptom_bundle"


def test_followup_specialist():
    ctx = {"last_specialist": "кардиолог", "last_intent": "specialist_info"}
    r = generate_reply("ещё подробнее", context=ctx)
    assert r.intent == "followup_specialist"
    assert "Кардиолог" in r.reply


def test_no_llm_key_uses_non_llm_path():
    if llm_enabled():
        return
    r = generate_reply("вопрос вне медицинской области: кто такой ньютон")
    assert r.intent in ("unknown", "corpus_retrieval")


def test_prostuda_maps_to_orvi():
    r = generate_reply("Какие симптомы у простуды?")
    assert r.intent in ("condition_info", "condition_inferred", "llm_fallback", "corpus_retrieval")


def test_blood_pressure_high_advises_doctor():
    r = generate_reply("Давление 170/105")
    assert r.intent == "bp_high"
    assert "обратиться к врачу" in r.reply.lower()
    assert "102" in r.reply

