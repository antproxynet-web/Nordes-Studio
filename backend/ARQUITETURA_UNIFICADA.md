# Arquitetura Unificada - Backend Flask

## 🎯 Objetivo

Criar um **único backend Flask** profissional, escalável e previsível, consolidando as melhores funcionalidades de `app.py`, `app_new.py` e `app_refactored.py`.

---

## 📁 Estrutura de Pastas Final

```
backend/
├── app.py                      # ✅ APENAS entrypoint (iniciar servidor)
├── create_app.py               # ✅ Application Factory
├── config.py                   # ✅ Configurações centralizadas
├── extensions.py               # ✅ Extensões compartilhadas (db, cors, oauth)
├── socketio_events.py          # ✅ Eventos SocketIO (chat em tempo real)
│
├── models/                     # 📦 Modelos de dados
│   ├── __init__.py
│   ├── user.py                # ✅ User (com is_verified)
│   ├── book.py                # ✅ Book
│   ├── chat.py                # ✅ Message, UserStatus
│   └── config.py              # ✅ Config (chave-valor)
│
├── routes/                     # 🛣️ Blueprints de rotas
│   ├── __init__.py
│   ├── auth.py                # ✅ Login, signup, OAuth (SEM prefixo /api)
│   ├── user.py                # ✅ Perfil, username, foto
│   ├── books.py               # ✅ CRUD de livros
│   ├── chat.py                # ✅ API de chat (REST)
│   ├── admin_tools.py         # ✅ Ferramentas de admin
│   └── static_routes.py       # ✅ Servir frontend
│
├── services/                   # 🔧 Lógica de negócio
│   ├── __init__.py
│   ├── auth_service.py        # ✅ Autenticação, JWT, OAuth
│   ├── user_service.py        # ✅ Gerenciamento de usuários
│   └── book_service.py        # ✅ Gerenciamento de livros
│
├── utils/                      # 🛠️ Utilitários
│   ├── __init__.py
│   ├── decorators.py          # ✅ token_required, admin_required
│   └── helpers.py             # ✅ Funções auxiliares
│
├── migrations/                 # 🗄️ Migrações de banco (opcional)
├── instance/                   # 🗄️ Banco de dados SQLite
│   └── nordes_studio.db
└── uploads/                    # 📁 Arquivos enviados
```

---

## 🏗️ Componentes Principais

### 1. **app.py** (Entrypoint)

**Responsabilidade**: APENAS iniciar o servidor. Nada mais.

```python
"""
Entrypoint da aplicação Flask
"""
from create_app import create_app, socketio

# Criar aplicação
app = create_app('development')

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor Nordes Studio iniciado")
    print("=" * 60)
    print("📍 URL: http://localhost:5000")
    print("🔐 JWT: Autenticação habilitada")
    print("💬 SocketIO: Chat em tempo real ativo")
    print("=" * 60)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
```

**Tamanho**: ~15 linhas  
**Princípio**: Single Responsibility

---

### 2. **create_app.py** (Application Factory)

**Responsabilidade**: Criar e configurar a aplicação Flask.

```python
"""
Application Factory - Nordes Studio
"""
import os
from flask import Flask
from flask_socketio import SocketIO
from config import get_config
from extensions import db, cors, oauth

# Instância global do SocketIO
socketio = None

def create_app(config_name=None):
    """
    Factory para criar a aplicação Flask
    
    Args:
        config_name: 'development', 'production', 'testing'
    
    Returns:
        Flask app configurada
    """
    global socketio
    
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
    
    # Registrar blueprints
    register_blueprints(app, google)
    
    # Registrar error handlers
    register_error_handlers(app)
    
    # Inicializar SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)
    
    # Registrar eventos SocketIO
    register_socketio_events(socketio, app)
    
    # Criar pasta de uploads
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    return app

def register_blueprints(app, google):
    """Registra todos os blueprints"""
    from routes.auth import auth_bp, oauth_bp, init_google_oauth
    from routes.user import user_bp
    from routes.books import books_bp
    from routes.chat import chat_bp
    from routes.admin_tools import admin_tools_bp
    from routes.static_routes import static_bp
    
    # Inicializar Google OAuth
    init_google_oauth(google)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)      # /api/signup, /api/login
    app.register_blueprint(oauth_bp)     # /login/google, /authorize/google (SEM /api)
    app.register_blueprint(user_bp)      # /api/user/*
    app.register_blueprint(books_bp)     # /api/books/*
    app.register_blueprint(chat_bp)      # /api/chat/*
    app.register_blueprint(admin_tools_bp)  # /api/admin/*
    app.register_blueprint(static_bp)    # /, /pages/*, /assets/*

def register_error_handlers(app):
    """Registra handlers de erro"""
    from flask import render_template_string
    
    def render_error_page(code, title, message):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(base_dir, '..', 'frontend', 'pages', 'error.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            return render_template_string(template, code=code, title=title, message=message), code
        except:
            return f"<h1>Erro {code}: {title}</h1><p>{message}</p>", code
    
    @app.errorhandler(404)
    def not_found(e):
        return render_error_page(404, "Não Encontrado", 
                                "A página que você procura não existe ou foi movida.")
    
    @app.errorhandler(500)
    def server_error(e):
        return render_error_page(500, "Erro Interno", 
                                "Ocorreu um erro inesperado. Tente novamente mais tarde.")
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_error_page(403, "Acesso Negado", 
                                "Você não tem permissão para acessar este recurso.")

def register_socketio_events(socketio, app):
    """Registra eventos SocketIO"""
    from socketio_events import register_events
    register_events(socketio, app)
```

---

### 3. **socketio_events.py** (Eventos SocketIO)

**Responsabilidade**: Gerenciar eventos de chat em tempo real.

```python
"""
Eventos SocketIO para chat em tempo real
"""
import jwt
from flask import request
from flask_socketio import emit, join_room
from datetime import datetime
from extensions import db
from models.user import User
from models.chat import Message

# Dicionário de usuários online: {user_id: sid}
online_users = {}

def register_events(socketio, app):
    """Registra todos os eventos SocketIO"""
    
    @socketio.on('connect')
    def handle_connect():
        """Evento de conexão do cliente"""
        token = request.args.get('token')
        if not token:
            return False  # Rejeitar conexão
        
        try:
            with app.app_context():
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                user_id = data['user_id']
                
                # Registrar usuário online
                online_users[user_id] = request.sid
                
                # Atualizar status no banco
                user = User.query.get(user_id)
                if user:
                    user.is_online = True
                    user.last_seen = datetime.utcnow()
                    db.session.commit()
                
                # Entrar na sala do usuário
                join_room(f"user_{user_id}")
                
                # Notificar todos que o usuário está online
                emit('user_status', {'user_id': user_id, 'status': 'online'}, broadcast=True)
                
                print(f"✅ Usuário {user_id} conectado via WebSocket")
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Evento de desconexão do cliente"""
        user_id = None
        for uid, sid in online_users.items():
            if sid == request.sid:
                user_id = uid
                break
        
        if user_id:
            with app.app_context():
                del online_users[user_id]
                
                user = User.query.get(user_id)
                if user:
                    user.is_online = False
                    user.last_seen = datetime.utcnow()
                    db.session.commit()
                
                emit('user_status', {'user_id': user_id, 'status': 'offline'}, broadcast=True)
                print(f"🔴 Usuário {user_id} desconectado")
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Evento de envio de mensagem"""
        sender_sid = request.sid
        sender_id = None
        
        for uid, sid in online_users.items():
            if sid == sender_sid:
                sender_id = uid
                break
        
        if not sender_id:
            return
        
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        
        if receiver_id and content:
            with app.app_context():
                # Salvar mensagem no banco
                new_msg = Message(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    content=content
                )
                db.session.add(new_msg)
                db.session.commit()
                
                msg_dict = new_msg.to_dict()
                
                # Enviar para o destinatário se estiver online
                emit('new_message', msg_dict, room=f"user_{receiver_id}")
                
                # Confirmar para o remetente
                emit('message_sent', msg_dict)
    
    @socketio.on('mark_read')
    def handle_mark_read(data):
        """Evento de marcação de mensagem como lida"""
        message_id = data.get('message_id')
        
        with app.app_context():
            msg = Message.query.get(message_id)
            if msg:
                msg.is_read = True
                db.session.commit()
                emit('message_read', {'message_id': message_id}, room=f"user_{msg.sender_id}")
```

---

### 4. **routes/auth.py** (Autenticação)

**Mudança Crítica**: Separar rotas OAuth em blueprint sem prefixo `/api`.

```python
"""
Rotas de Autenticação
"""
import json
import urllib.parse
from flask import Blueprint, request, jsonify, session, redirect, url_for
from services.auth_service import AuthService

# Blueprint para rotas API (/api/signup, /api/login)
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# Blueprint separado para OAuth (SEM prefixo /api)
oauth_bp = Blueprint('oauth', __name__)

# Instância do Google OAuth (será inicializada no create_app)
google = None

def init_google_oauth(oauth_instance):
    """Inicializa o Google OAuth"""
    global google
    google = oauth_instance

# --- ROTAS API ---

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Cadastro de novo usuário"""
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    name = f"{data.get('firstname', '')} {data.get('lastname', '')}".strip()
    phone = data.get('phone')
    
    if not email or not password:
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
    
    user, error = AuthService.create_user(email, password, name, phone, username)
    
    if error:
        return jsonify({'message': error}), 400
    
    token = AuthService.generate_token(user)
    
    return jsonify({
        'message': 'Conta criada com sucesso',
        'token': token,
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login de usuário"""
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
    
    user, error = AuthService.authenticate_user(email, password)
    
    if error:
        return jsonify({'message': error}), 401
    
    token = AuthService.generate_token(user)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    })

@auth_bp.route('/logout')
def logout():
    """Logout de usuário"""
    session.pop('user_id', None)
    return jsonify({"success": True})

# --- ROTAS OAUTH (SEM PREFIXO /api) ---

@oauth_bp.route('/login/google')
def login_google():
    """Inicia o fluxo de autenticação com Google"""
    if not google:
        return jsonify({'message': 'OAuth não configurado'}), 500
    
    redirect_uri = url_for('oauth.authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@oauth_bp.route('/authorize/google')
def authorize_google():
    """Callback do OAuth Google"""
    if not google:
        return redirect('/pages/login.html?error=oauth_not_configured')
    
    try:
        token_data = google.authorize_access_token()
        user_info = token_data.get('userinfo')
        
        if not user_info:
            resp = google.get('https://www.googleapis.com/oauth2/v3/userinfo')
            user_info = resp.json()
        
        user = AuthService.create_or_update_oauth_user(
            email=user_info['email'],
            name=user_info.get('name'),
            picture=user_info.get('picture')
        )
        
        if not user:
            return redirect('/pages/login.html?error=oauth_user_creation_failed')
        
        # Gerar token JWT (NÃO usar session)
        token = AuthService.generate_token(user)
        
        # Redirecionar para home com token
        params = urllib.parse.urlencode({
            'login_success': 'true',
            'token': token,
            'user': json.dumps(user.to_dict())
        })
        
        return redirect(f"/pages/home.html?{params}")
        
    except Exception as e:
        print(f"❌ Erro no OAuth: {e}")
        error_msg = urllib.parse.quote(str(e))
        return redirect(f'/pages/login.html?error=oauth_failed&details={error_msg}')
```

---

### 5. **models/user.py** (Modelo de Usuário)

**Mudança**: Adicionar campo `is_verified`.

```python
"""
Modelo de Usuário
"""
from extensions import db

class User(db.Model):
    """Modelo de usuário do sistema"""
    
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255))  # Hash da senha (pode ser NULL para OAuth)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, index=True)
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    picture = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')  # user, professional, admin
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=db.func.now())
    
    # ✅ NOVO: Sistema de verificação
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self, include_sensitive=False):
        """Converte o usuário para dicionário"""
        picture_url = self._normalize_picture_url(self.picture)
        
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'username': self.username,
            'phone': self.phone,
            'bio': self.bio,
            'picture': picture_url,
            'role': self.role,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_verified': self.is_verified,  # ✅ NOVO
            'verified_at': self.verified_at.isoformat() if self.verified_at else None  # ✅ NOVO
        }
        
        if include_sensitive:
            data['password'] = self.password
        
        return data
    
    def _normalize_picture_url(self, picture):
        """Normaliza URL de foto de perfil"""
        if not picture:
            return None
        
        if picture.startswith('http://') or picture.startswith('https://'):
            return picture
        
        if picture.startswith('/uploads/'):
            return picture
        
        return f'/uploads/{picture}'
    
    def __repr__(self):
        return f'<User {self.email}>'
```

---

## 🔐 Fluxo de Autenticação Unificado

### Login Tradicional (Email/Senha)

```
1. Frontend envia POST /api/login com {email, password}
2. AuthService.authenticate_user() valida credenciais (com hash)
3. AuthService.generate_token() cria JWT
4. Backend retorna {token, user}
5. Frontend armazena token no localStorage
6. Todas as requisições subsequentes incluem: Authorization: Bearer <token>
```

### Login com Google OAuth

```
1. Frontend redireciona para /login/google
2. Google autentica o usuário
3. Google redireciona para /authorize/google
4. AuthService.create_or_update_oauth_user() cria/atualiza usuário
5. AuthService.generate_token() cria JWT
6. Backend redireciona para /pages/home.html?token=<jwt>&user=<json>
7. Frontend extrai token da URL e armazena no localStorage
```

**Importante**: Não usar `session` para armazenar autenticação. JWT é a única fonte de verdade.

---

## ✅ Checklist de Implementação

- [ ] Criar `create_app.py` com Application Factory
- [ ] Criar `socketio_events.py` com eventos de chat
- [ ] Separar rotas OAuth em blueprint sem prefixo `/api`
- [ ] Adicionar campos `is_verified` e `verified_at` ao modelo User
- [ ] Criar endpoint `/api/admin/verify-user/<user_id>` (admin only)
- [ ] Migrar senhas em texto plano para hash (script de migração)
- [ ] Deletar `app_new.py` e `config_app.py`
- [ ] Renomear `app_refactored.py` para `create_app.py`
- [ ] Simplificar `app.py` para apenas entrypoint
- [ ] Testar login tradicional
- [ ] Testar Google OAuth
- [ ] Testar chat em tempo real
- [ ] Testar validação de username
- [ ] Testar sistema de verificação
- [ ] Documentar contratos de API

---

## 📊 Contratos de API

### Autenticação

| Endpoint            | Método | Auth | Descrição                |
|---------------------|--------|------|--------------------------|
| `/api/signup`       | POST   | ❌   | Criar nova conta         |
| `/api/login`        | POST   | ❌   | Login com email/senha    |
| `/api/logout`       | GET    | ❌   | Logout                   |
| `/login/google`     | GET    | ❌   | Iniciar OAuth Google     |
| `/authorize/google` | GET    | ❌   | Callback OAuth Google    |

### Usuário

| Endpoint                      | Método | Auth | Descrição                    |
|-------------------------------|--------|------|------------------------------|
| `/api/user/profile`           | GET    | ✅   | Obter perfil do usuário      |
| `/api/user/profile`           | PUT    | ✅   | Atualizar perfil             |
| `/api/user/profile-picture`   | POST   | ✅   | Upload de foto de perfil     |
| `/api/user/check-username`    | GET    | ✅   | Validar disponibilidade      |

### Chat

| Endpoint                        | Método | Auth | Descrição                    |
|---------------------------------|--------|------|------------------------------|
| `/api/chat/users`               | GET    | ✅   | Listar usuários para chat    |
| `/api/chat/messages/<user_id>`  | GET    | ✅   | Obter mensagens com usuário  |
| `/api/chat/send`                | POST   | ✅   | Enviar mensagem (REST)       |
| `/api/chat/user/<user_id>`      | GET    | ✅   | Obter informações de usuário |

### Admin

| Endpoint                          | Método | Auth       | Descrição                |
|-----------------------------------|--------|------------|--------------------------|
| `/api/admin/verify-user/<id>`     | POST   | ✅ (admin) | Marcar usuário verificado|
| `/api/admin/unverify-user/<id>`   | POST   | ✅ (admin) | Remover verificação      |

---

## 🚀 Como Executar

```bash
# 1. Ativar ambiente virtual (se houver)
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar aplicação
python app.py

# 4. Acessar
# Frontend: http://localhost:5000
# API: http://localhost:5000/api
```

---

**Gerado em**: 01/02/2026  
**Versão**: 1.0  
**Status**: Pronto para implementação
