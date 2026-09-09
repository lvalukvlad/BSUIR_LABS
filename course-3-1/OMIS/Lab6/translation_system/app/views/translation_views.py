from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from app.controllers.translation_controller import TranslationController
from app.models.context import Context
from app.views.auth_views import require_auth
import os

translation_bp = Blueprint('translation', __name__)
trans_controller = TranslationController()


@translation_bp.route('/translate', methods=['GET', 'POST'])
@require_auth
def translate():
    result = None
    if request.method == 'POST':
        content = request.form.get('content', '').strip()

        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and file.filename.endswith('.txt'):
                content = file.read().decode('utf-8').strip()

        if not content:
            flash("Введите текст или загрузите файл.")
            return render_template('translate.html', result=result)

        source_lang = request.form['source_lang']
        target_lang = request.form['target_lang']
        dialect = request.form.get('dialect', '')
        style = request.form.get('style', 'neutral')

        if style == 'literal':
            translation_type = 'literal'
        elif style == 'poetic':
            translation_type = 'creative'
        else:
            translation_type = 'adaptive'

        context = Context(style=style, translation_type=translation_type)

        text_id = trans_controller.process_text(content, source_lang, context.__dict__)
        trans_id, draft = trans_controller.generate_draft(text_id, target_lang, dialect)

        trans_controller.translations.append({
            'trans_id': trans_id,
            'text_id': text_id,
            'content': content,
            'draft': draft,
            'final_version': '',
            'status': 'draft',
            'user_id': session.get('user_id'),
            'username': session.get('user'),
            'created_at': __import__('datetime').datetime.now().isoformat()
        })
        from app.services.storage_service import StorageService
        StorageService.save_json('translations.json', trans_controller.translations)

        result = draft
        form_data = {
            'content': content,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'style': style,
            'dialect': dialect
        }
        return render_template('translate.html', result=result, form_data=form_data)

    return render_template('translate.html', result=result, form_data={})


@translation_bp.route('/edit-draft/<trans_id>', methods=['GET', 'POST'])
@require_auth
def edit_draft(trans_id):
    trans = next((t for t in trans_controller.translations if t['trans_id'] == trans_id), None)
    if not trans:
        flash('Перевод не найден')
        return redirect(url_for('translation.dashboard'))

    if request.method == 'POST':
        new_draft = request.form['draft']
        trans['draft'] = new_draft
        from app.services.storage_service import StorageService
        StorageService.save_json('translations.json', trans_controller.translations)
        flash('Черновик обновлён')
        return redirect(url_for('translation.dashboard'))

    return render_template('edit_draft.html', translation=trans)


@translation_bp.route('/dashboard')
@require_auth
def dashboard():
    from app.services.storage_service import StorageService
    all_translations = StorageService.load_json('translations.json', [])
    user_id = session.get('user_id')
    username = session.get('user')
    
    user_translations = [
        t for t in all_translations 
        if t.get('user_id') == user_id or t.get('username') == username
    ]
    
    return render_template('dashboard.html', translations=user_translations, username=username)

@translation_bp.route('/localize/<trans_id>', methods=['GET', 'POST'])
@require_auth
def localize(trans_id):
    from app.controllers.localization_controller import LocalizationController
    trans = next((t for t in trans_controller.translations if t['trans_id'] == trans_id), None)
    if not trans:
        flash('Перевод не найден')
        return redirect(url_for('translation.dashboard'))
    
    if request.method == 'POST':
        chosen_variant = request.form.get('chosen_variant', '')
        custom_variant = request.form.get('custom_variant', '')
        
        if custom_variant:
            final_text = custom_variant
        elif chosen_variant:
            final_text = chosen_variant.split('] ', 1)[1] if '] ' in chosen_variant else chosen_variant
        else:
            flash('Выберите вариант или введите свой')
            return redirect(url_for('translation.localize', trans_id=trans_id))
        
        trans['final_version'] = final_text
        trans['status'] = 'localized'
        from app.services.storage_service import StorageService
        StorageService.save_json('translations.json', trans_controller.translations)
        flash('Вариант перевода утверждён. Теперь вы можете просмотреть и утвердить финальную версию.')
        return redirect(url_for('translation.view_final', trans_id=trans_id))
    
    original_context = trans.get('context', {})
    variants = LocalizationController.generate_variants(trans['draft'], original_context)
    return render_template('localize.html', translation=trans, variants=variants)


@translation_bp.route('/graph')
@require_auth
def view_graph():
    from app.services.storage_service import StorageService
    graph = StorageService.load_json('knowledge_graph.json', {})
    return render_template('graph.html', graph=graph)

@translation_bp.route('/final/<trans_id>', methods=['GET', 'POST'])
@require_auth
def view_final(trans_id):
    trans = next((t for t in trans_controller.translations if t['trans_id'] == trans_id), None)
    if not trans:
        flash('Перевод не найден')
        return redirect(url_for('translation.dashboard'))
    
    user_id = session.get('user_id')
    username = session.get('user')
    if trans.get('user_id') != user_id and trans.get('username') != username:
        flash('У вас нет доступа к этому переводу')
        return redirect(url_for('translation.dashboard'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'approve':
            trans['status'] = 'approved'
            flash('Перевод утверждён')
        elif action == 'reject':
            trans['status'] = 'draft'
            trans['final_version'] = ''
            flash('Перевод отклонён, возвращён в черновик')
        elif action == 'edit_final':
            new_final = request.form.get('final_version', '').strip()
            if new_final:
                trans['final_version'] = new_final
                flash('Финальная версия обновлена')
        
        from app.services.storage_service import StorageService
        StorageService.save_json('translations.json', trans_controller.translations)
        return redirect(url_for('translation.view_final', trans_id=trans_id))
    
    return render_template('final_translation.html', translation=trans)