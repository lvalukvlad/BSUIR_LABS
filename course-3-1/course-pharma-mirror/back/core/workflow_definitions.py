"""Упрощенные определения workflow"""
from core.workflow_engine import WorkflowNode
def create_diagnosis_workflow(agents: dict):
    """Workflow для диагностики - упрощенный"""
    return [
        WorkflowNode(
            name="diagnosis_core",
            agent=agents.get("diagnostician"),
            description="Основная диагностика",
            timeout=120,
            retries=1
        )
    ]

def create_treatment_workflow(agents: dict):
    """Workflow для лечения - упрощенный"""
    workflow_nodes = [
        WorkflowNode(
            name="medicine_recommendation",
            agent=agents.get("medicine_provider"),
            description="Рекомендации по лекарствам",
            timeout=120,
            retries=1
        ),
        WorkflowNode(
            name="response_formatting",
            agent=agents.get("response_formatter"),
            description="Форматирование ответа",
            timeout=120,
            retries=1
        )
    ]

    # Добавляем treatment_planning только если есть агент
    if agents.get("treatment_planner"):
        workflow_nodes.insert(1, WorkflowNode(
            name="treatment_planning",
            agent=agents.get("treatment_planner"),
            description="Планирование лечения",
            timeout=120,
            retries=1
        ))

    return workflow_nodes

def get_all_workflow_definitions(agents: dict) -> dict:
    """Возвращает все определения workflow"""
    workflows = {}

    # Базовые workflow
    workflows["diagnosis"] = create_diagnosis_workflow(agents)
    workflows["treatment"] = create_treatment_workflow(agents)

    return workflows