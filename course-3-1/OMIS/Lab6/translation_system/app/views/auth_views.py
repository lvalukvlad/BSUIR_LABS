from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import uuid
from datetime import datetime, timedelta
from app.services.storage_service import StorageService

auth_bp = Blueprint('auth', __name__)

def get_users():
    users_data = StorageService.load_json('users.json', {})
    if not users_data:
        default_users = {
            'translator1': {
                'password_hash': generate_password_hash('translator123'),
                'role': 'translator',
                'user_id': str(uuid.uuid4())
            },
            'editor1': {
                'password_hash': generate_password_hash('editor123'),
                'role': 'editor',
                'user_id': str(uuid.uuid4())
            },
            'admin1': {
                'password_hash': generate_password_hash('admin123'),
                'role': 'admin',
                'user_id': str(uuid.uuid4())
            }
        }
        StorageService.save_json('users.json', default_users)
        return default_users
    return users_data

TOKENS = {}

def generate_access_token(username, user_id):
    token = secrets.token_urlsafe(32)
    TOKENS[token] = {
        'username': username,
        'user_id': user_id,
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
    }
    return token

def validate_token(token):
    if token not in TOKENS:
        return None
    token_data = TOKENS[token]
    expires_at = datetime.fromisoformat(token_data['expires_at'])
    if datetime.now() > expires_at:
        del TOKENS[token]
        return None
    return token_data

@auth_bp.route('/')
def index():
    if 'user' in session:
        from app.services.storage_service import StorageService
        all_translations = StorageService.load_json('translations.json', [])
        user_id = session.get('user_id')
        username = session.get('user')
        user_translations = [
            t for t in all_translations 
            if t.get('user_id') == user_id or t.get('username') == username
        ]
        normalized = []
        for t in user_translations:
            if not isinstance(t, dict):
                continue
            item = dict(t)
            if 'content' not in item:
                item['content'] = item.get('draft', '')
            if item.get('final_version') is None:
                item['final_version'] = ''
            normalized.append(item)
        return render_template('index.html', translations=normalized[:5])
    else:
        return render_template('index.html', translations=[])

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error="Введите имя пользователя и пароль")
        
        users = get_users()
        if username not in users:
            return render_template('login.html', error="Неверное имя пользователя или пароль")
        
        user_data = users[username]
        if not check_password_hash(user_data['password_hash'], password):
            return render_template('login.html', error="Неверное имя пользователя или пароль")
        
        session['user'] = username
        session['role'] = user_data['role']
        session['user_id'] = user_data['user_id']
        
        access_token = generate_access_token(username, user_data['user_id'])
        session['access_token'] = access_token
        
        return redirect(url_for('translation.dashboard'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    if 'access_token' in session:
        token = session['access_token']
        if token in TOKENS:
            del TOKENS[token]
    session.clear()
    return redirect(url_for('auth.login'))

def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function