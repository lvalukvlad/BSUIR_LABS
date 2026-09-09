from flask import Blueprint, request, jsonify
from app.controllers.translation_controller import TranslationController
from app.knowledge.knowledge_graph import KnowledgeGraphService

api_bp = Blueprint('api', __name__)
trans_controller = TranslationController()
kg_service = KnowledgeGraphService()


@api_bp.route('/api/translate', methods=['POST'])
def api_translate():
    data = request.json
    content = data.get('content', '')
    context = data.get('context', {})
    dialect = data.get('dialect', '')

    text_id = trans_controller.process_text(content, 'auto', context)  # ← auto
    trans_id, draft = trans_controller.generate_draft(text_id, 'en', dialect)
   
    if draft.startswith("[INFO]"):
        return jsonify({
            "trans_id": trans_id,
            "message": draft,
            "draft": content
        })

    return jsonify({
        "trans_id": trans_id,
        "draft": draft
    })


@api_bp.route('/api/graph', methods=['GET'])
def api_graph():
    return jsonify(kg_service.graph)