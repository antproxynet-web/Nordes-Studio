"""
Rotas para servir arquivos estáticos - Versão Corrigida
"""
from flask import Blueprint, send_from_directory

static_bp = Blueprint('static', __name__)

@static_bp.route('/')
def index():
    """Página inicial"""
    return send_from_directory('../frontend/pages', 'index.html')

@static_bp.route('/chat.html')
def serve_chat_root():
    """Servir chat.html da raiz ou de pages"""
    return send_from_directory('../frontend/pages', 'chat.html')

@static_bp.route('/real-chat.html')
def serve_real_chat_root():
    """Servir real-chat.html da raiz ou de pages"""
    return send_from_directory('../frontend/pages', 'real-chat.html')

@static_bp.route('/pages/<path:path>')
def serve_pages(path):
    """Servir qualquer página HTML da pasta pages"""
    return send_from_directory('../frontend/pages', path)

@static_bp.route('/assets/<path:path>')
def serve_assets(path):
    """Servir assets (CSS, JS, imagens)"""
    return send_from_directory('../frontend/assets', path)

@static_bp.route('/uploads/<path:path>')
def serve_uploads(path):
    """Servir uploads (imagens de livros, perfis, chat)"""
    # O Flask já lida com subdiretórios se passarmos a pasta base 'uploads'
    return send_from_directory('uploads', path)

@static_bp.route('/<path:path>')
def serve_static(path):
    """Fallback para outros arquivos estáticos"""
    if path.endswith('.html'):
        return send_from_directory('../frontend/pages', path)
    return send_from_directory('../frontend', path)
