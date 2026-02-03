"""
Application Factory - Nordes Studio
Arquitetura unificada com Application Factory, Blueprints e SocketIO
"""
import os
from flask import Flask, render_template_string
from flask_socketio import SocketIO
from config import get_config
from extensions import db, cors, oauth

# Instância global do SocketIO
socketio = SocketIO()

def create_app(config_name=None):
    """
    Factory para criar a aplicação Flask
    
    Args:
        config_name: 'development', 'production', 'testing'
    
    Returns:
        Flask app configurada
    """
    # Permitir OAUTHLIB em HTTP (apenas desenvolvimento)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    app = Flask(__name__)
    
    # Carregar configuração
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Inicializar extensões
    db.init_app(app)
    cors.init_app(app, 
                  origins=app.config['CORS_ORIGINS'],
                  supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'])
    oauth.init_app(app)
    
    # Configurar OAuth Google
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    # Criar banco de dados
    with app.app_context():
        db.create_all()
        print("✓ Banco de dados inicializado")
    
    # Registrar blueprints
    register_blueprints(app, google)
    
    # Registrar error handlers
    register_error_handlers(app)
    
    # Inicializar SocketIO
    socketio.init_app(app, cors_allowed_origins="*", manage_session=False)
    print("✓ SocketIO inicializado")
    
    # Registrar eventos SocketIO
    register_socketio_events(socketio, app)
    
    # Criar pasta de uploads
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        print(f"✓ Pasta de uploads criada: {app.config['UPLOAD_FOLDER']}")
    
    return app

def register_blueprints(app, google):
    """
    Registra todos os blueprints da aplicação
    
    Args:
        app: Aplicação Flask
        google: Instância do Google OAuth
    """
    from routes.auth import auth_bp, oauth_bp, init_google_oauth
    from routes.user import user_bp
    from routes.books import books_bp
    from routes.chat import chat_bp
    from routes.admin_tools import admin_tools_bp
    from routes.static_routes import static_bp
    
    # Inicializar Google OAuth
    init_google_oauth(google)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)         # /api/signup, /api/login
    app.register_blueprint(oauth_bp)        # /login/google, /authorize/google (SEM /api)
    app.register_blueprint(user_bp)         # /api/user/*
    app.register_blueprint(books_bp)        # /api/books/*
    app.register_blueprint(chat_bp)         # /api/chat/*
    app.register_blueprint(admin_tools_bp)  # /api/admin/*
    app.register_blueprint(static_bp)       # /, /pages/*, /assets/*
    
    print("✓ Blueprints registrados")

def register_error_handlers(app):
    """
    Registra handlers de erro personalizados
    
    Args:
        app: Aplicação Flask
    """
    def render_error_page(code, title, message):
        """Renderiza página de erro personalizada"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(base_dir, '..', 'frontend', 'pages', 'error.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            return render_template_string(template, code=code, title=title, message=message), code
        except Exception as e:
            print(f"Erro ao renderizar página de erro: {e}")
            return f"<h1>Erro {code}: {title}</h1><p>{message}</p>", code
    
    @app.errorhandler(404)
    def not_found(e):
        return render_error_page(404, "Não Encontrado", 
                                "A página que você procura não existe ou foi movida.")
    
    @app.errorhandler(500)
    def server_error(e):
        return render_error_page(500, "Erro Interno", 
                                "Ocorreu um erro inesperado em nosso servidor. Tente novamente mais tarde.")
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_error_page(403, "Acesso Negado", 
                                "Você não tem permissão para acessar este recurso.")
    
    @app.errorhandler(400)
    def bad_request(e):
        return render_error_page(400, "Requisição Inválida", 
                                "A requisição enviada é inválida ou está malformada.")
    
    print("✓ Error handlers registrados")

def register_socketio_events(socketio, app):
    """
    Registra eventos SocketIO
    
    Args:
        socketio: Instância do SocketIO
        app: Aplicação Flask
    """
    from socketio_events import register_events
    register_events(socketio, app)
    print("✓ Eventos SocketIO registrados")
