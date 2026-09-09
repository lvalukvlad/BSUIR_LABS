import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("medical_chatbot")

def has_meaningful_symptoms(symptoms: list, min_length=5) -> bool:
    return any(len(s.strip()) > min_length for s in symptoms)

def is_vague_diagnosis(diagnosis: str) -> bool:
    vague_terms = ['требуется', 'обследование', 'неизвестно', 'неопределен', 'симптомы', 'уточнение']
    return any(term in diagnosis.lower() for term in vague_terms) or len(diagnosis.split()) < 3