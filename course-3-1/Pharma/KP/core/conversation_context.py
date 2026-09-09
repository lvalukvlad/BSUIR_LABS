from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConversationStage(Enum):
    GREETING = "greeting"
    CONTRAINDICATIONS_COLLECTION = "contraindications_collection"
    SYMPTOM_COLLECTION = "symptom_collection"
    LOCALIZATION_ANALYSIS = "localization_analysis"
    CLARIFICATION = "clarification"
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class LocalizationInfo:
    primary_location: Optional[str] = None
    specific_locations: List[str] = field(default_factory=list)
    laterality: Optional[str] = None
    radiation: List[str] = field(default_factory=list)
    depth: Optional[str] = None
    anatomical_system: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


localization_info: LocalizationInfo = field(default_factory=LocalizationInfo)
localization_analysis: Optional[Dict[str, Any]] = None

@dataclass
class SymptomInfo:
    description: str
    normalized: Optional[str] = None
    location: Optional[str] = None
    intensity: Optional[str] = None
    duration: Optional[str] = None
    onset: Optional[str] = None
    frequency: Optional[str] = None
    triggers: List[str] = field(default_factory=list)
    alleviating_factors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DiagnosisInfo:
    name: str
    confidence: float
    icd10_code: Optional[str] = None
    differential_diagnosis: List[str] = field(default_factory=list)
    supporting_evidence: List[str] = field(default_factory=list)
    conflicting_evidence: List[str] = field(default_factory=list)
    needs_clarification: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MedicineInfo:
    name: str
    mechanism: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    effectiveness: Optional[float] = None
    contraindications: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserProfile:
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    allergies: List[str] = field(default_factory=list)
    chronic_conditions: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    smoking: Optional[bool] = None
    alcohol: Optional[str] = None
    pregnancy: Optional[bool] = None
    breastfeeding: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContraindicationInfo:
    allergies: List[str] = field(default_factory=list)
    chronic_conditions: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    pregnancy: Optional[bool] = None
    breastfeeding: Optional[bool] = None
    kidney_problems: Optional[bool] = None
    liver_problems: Optional[bool] = None
    other_restrictions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConversationContext:
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    user_profile: UserProfile = field(default_factory=UserProfile)

    symptoms: List[SymptomInfo] = field(default_factory=list)
    symptom_texts: List[str] = field(default_factory=list)

    diagnoses: List[DiagnosisInfo] = field(default_factory=list)
    primary_diagnosis: Optional[DiagnosisInfo] = None
    localizations: List[str] = field(default_factory=list)

    suggested_medicines: List[MedicineInfo] = field(default_factory=list)
    treatment_plan: Optional[str] = None

    severity_assessment: Optional[Dict[str, Any]] = None
    contraindications: List[Dict[str, Any]] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)

    contraindications: ContraindicationInfo = field(default_factory=ContraindicationInfo)

    contraindications_collected: bool = False
    symptoms_collected: bool = False

    max_clarification_attempts: int = 2
    clarification_attempts_count: int = 0

    workflow_id: Optional[str] = None
    current_stage: ConversationStage = ConversationStage.GREETING
    needs_clarification: bool = False
    clarification_questions: List[str] = field(default_factory=list)
    clarification_attempts: int = 0

    messages: List[Dict[str, str]] = field(default_factory=list)
    agent_execution_history: List[Dict[str, Any]] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    language: str = "ru"

    def to_dict(self) -> Dict[str, Any]:
        result = {}

        try:
            result["conversation_id"] = self.conversation_id
            result["user_id"] = self.user_id
            result["session_id"] = self.session_id

            if hasattr(self, 'user_profile') and self.user_profile is not None:
                if hasattr(self.user_profile, 'to_dict'):
                    result["user_profile"] = self.user_profile.to_dict()
                elif hasattr(self.user_profile, '__dict__'):
                    result["user_profile"] = self.user_profile.__dict__
                else:
                    result["user_profile"] = {}

            result["symptoms"] = []
            if hasattr(self, 'symptoms'):
                for symptom in self.symptoms:
                    if hasattr(symptom, 'to_dict'):
                        result["symptoms"].append(symptom.to_dict())
                    elif isinstance(symptom, dict):
                        result["symptoms"].append(symptom)
                    else:
                        result["symptoms"].append(str(symptom))

            result["symptom_texts"] = getattr(self, 'symptom_texts', []).copy()

            result["diagnoses"] = []
            if hasattr(self, 'diagnoses'):
                for diagnosis in self.diagnoses:
                    if hasattr(diagnosis, 'to_dict'):
                        result["diagnoses"].append(diagnosis.to_dict())
                    elif isinstance(diagnosis, dict):
                        result["diagnoses"].append(diagnosis)
                    else:
                        result["diagnoses"].append(str(diagnosis))

            if hasattr(self, 'primary_diagnosis') and self.primary_diagnosis:
                if hasattr(self.primary_diagnosis, 'to_dict'):
                    result["primary_diagnosis"] = self.primary_diagnosis.to_dict()
                elif hasattr(self.primary_diagnosis, '__dict__'):
                    result["primary_diagnosis"] = self.primary_diagnosis.__dict__
                else:
                    result["primary_diagnosis"] = str(self.primary_diagnosis)

            result["suggested_medicines"] = []
            if hasattr(self, 'suggested_medicines'):
                for med in self.suggested_medicines:
                    if hasattr(med, 'to_dict'):
                        result["suggested_medicines"].append(med.to_dict())
                    elif isinstance(med, dict):
                        result["suggested_medicines"].append(med)
                    else:
                        result["suggested_medicines"].append(str(med))

            result["treatment_plan"] = getattr(self, 'treatment_plan', None)
            result["localizations"] = getattr(self, 'localizations', []).copy()
            result["red_flags"] = getattr(self, 'red_flags', []).copy()
            result["workflow_id"] = getattr(self, 'workflow_id', None)

            if hasattr(self, 'contraindications'):
                if hasattr(self.contraindications, 'to_dict'):
                    result["contraindications"] = self.contraindications.to_dict()
                elif hasattr(self.contraindications, '__dict__'):
                    result["contraindications"] = self.contraindications.__dict__
                else:
                    result["contraindications"] = self.contraindications

            if hasattr(self, 'current_stage'):
                if hasattr(self.current_stage, 'value'):
                    result["current_stage"] = self.current_stage.value
                else:
                    result["current_stage"] = str(self.current_stage)

            result["needs_clarification"] = getattr(self, 'needs_clarification', False)
            result["clarification_questions"] = getattr(self, 'clarification_questions', []).copy()
            result["clarification_attempts"] = getattr(self, 'clarification_attempts', 0)

            result["messages"] = getattr(self, 'messages', []).copy()
            result["agent_execution_history"] = getattr(self, 'agent_execution_history', []).copy()

            if hasattr(self, 'created_at'):
                if hasattr(self.created_at, 'isoformat'):
                    result["created_at"] = self.created_at.isoformat()
                else:
                    result["created_at"] = str(self.created_at)

            if hasattr(self, 'updated_at'):
                if hasattr(self.updated_at, 'isoformat'):
                    result["updated_at"] = self.updated_at.isoformat()
                else:
                    result["updated_at"] = str(self.updated_at)

            result["language"] = getattr(self, 'language', 'ru')

            dynamic_fields = [
                'normalized_symptoms', 'symptom_categories',
                'preliminary_diagnosis', 'normalization_success',
                'severity_assessment', 'contraindications_collected',
                'symptoms_collected', 'max_clarification_attempts',
                'clarification_attempts_count', 'localization_info',
                'localization_analysis'
            ]

            for field in dynamic_fields:
                if hasattr(self, field):
                    value = getattr(self, field)
                    if hasattr(value, 'to_dict'):
                        result[field] = value.to_dict()
                    elif hasattr(value, '__dict__'):
                        result[field] = value.__dict__
                    else:
                        result[field] = value

        except Exception as e:
            logger.error(f"Error in to_dict: {e}", exc_info=True)
            result = {
                "conversation_id": getattr(self, 'conversation_id', 'unknown'),
                "current_stage": getattr(self, 'current_stage', 'unknown'),
                "error": str(e)
            }

        return result

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == "current_stage":
                    if isinstance(value, ConversationStage):
                        setattr(self, key, value)
                    elif isinstance(value, str):
                        try:
                            stage = ConversationStage(value)
                            setattr(self, key, stage)
                        except ValueError:
                            logger.warning(f"Invalid stage value: {value}")
                    else:
                        logger.warning(f"Invalid type for current_stage: {type(value)}")
                else:
                    setattr(self, key, value)

        self.updated_at = datetime.now()

    def add_symptom(self, symptom_text: str, normalized: Optional[str] = None):
        symptom = SymptomInfo(description=symptom_text, normalized=normalized)
        self.symptoms.append(symptom)
        self.symptom_texts.append(symptom_text)
        self.updated_at = datetime.now()

    def add_diagnosis(self, diagnosis: DiagnosisInfo):
        self.diagnoses.append(diagnosis)
        if not self.primary_diagnosis or diagnosis.confidence > self.primary_diagnosis.confidence:
            self.primary_diagnosis = diagnosis
        self.updated_at = datetime.now()

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    def log_agent_execution(self, agent_name: str, input_data: Dict, output_data: Dict):
        self.agent_execution_history.append({
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "input": input_data,
            "output": output_data
        })
        self.updated_at = datetime.now()

    def get_symptom_text(self) -> str:
        return " ".join(self.symptom_texts)

    def get_normalized_symptoms(self) -> List[str]:
        normalized = []

        for symptom in self.symptoms:
            if isinstance(symptom, SymptomInfo):
                normalized.append(symptom.normalized or symptom.description)
            elif isinstance(symptom, dict):
                normalized.append(
                    symptom.get('normalized', symptom.get('text', symptom.get('description', str(symptom)))))
            else:
                normalized.append(str(symptom))

        return normalized

    def get_symptoms_for_processing(self) -> List[str]:
        result = []

        if hasattr(self, 'normalized_symptoms') and self.normalized_symptoms:
            for symptom in self.normalized_symptoms:
                if isinstance(symptom, dict):
                    result.append(symptom.get('normalized', symptom.get('text', '')))
                else:
                    result.append(str(symptom))

        if not result and self.symptom_texts:
            result = self.symptom_texts.copy()

        return result

    def has_sufficient_symptoms(self, min_count: int = 1) -> bool:
        return len(self.symptoms) >= min_count

    def needs_more_clarification(self, max_attempts: int = 3) -> bool:
        return self.needs_clarification and self.clarification_attempts < max_attempts

    def reset_clarification(self):
        self.needs_clarification = False
        self.clarification_questions = []

    def set_clarification_questions(self, questions: List[str]):
        self.clarification_questions = questions
        self.needs_clarification = len(questions) > 0

        if len(questions) > 0:
            self.clarification_attempts_count += 1
            logger.info(
                f"Set clarification questions (attempt {self.clarification_attempts_count}): {len(questions)} questions")

    def update_contraindications(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.contraindications, key):
                setattr(self.contraindications, key, value)

        self.contraindications_collected = True
        self.updated_at = datetime.now()