"""
Rotas de Autenticação
Separação entre rotas API (/api) e rotas OAuth (sem prefixo)
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
    """
    Inicializa o Google OAuth
    
    Args:
        oauth_instance: Instância do Google OAuth configurada
    """
    global google
    google = oauth_instance

# ==================== ROTAS API ====================

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Cadastro de novo usuário
    
    Body:
        {
            "email": "user@example.com",
            "password": "senha123",
            "firstname": "João",
            "lastname": "Silva",
            "phone": "11999999999",
            "username": "joaosilva" (opcional)
        }
    
    Returns:
        201: {message, token, user}
        400: {message} - Erro de validação
    """
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    name = f"{data.get('firstname', '')} {data.get('lastname', '')}".strip()
    phone = data.get('phone')
    
    if not email or not password:
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
    
    # Criar usuário
    user, error = AuthService.create_user(email, password, name, phone, username)
    
    if error:
        return jsonify({'message': error}), 400
    
    # Gerar token JWT
    token = AuthService.generate_token(user)
    
    return jsonify({
        'message': 'Conta criada com sucesso',
        'token': token,
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login de usuário
    
    Body:
        {
            "email": "user@example.com",
            "password": "senha123"
        }
    
    Returns:
        200: {token, user}
        401: {message} - Credenciais inválidas
    """
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
    
    # Autenticar usuário
    user, error = AuthService.authenticate_user(email, password)
    
    if error:
        return jsonify({'message': error}), 401
    
    # Gerar token JWT
    token = AuthService.generate_token(user)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    })

@auth_bp.route('/logout')
def logout():
    """
    Logout de usuário
    
    Limpa a sessão (se existir)
    
    Returns:
        200: {success: true}
    """
    session.pop('user_id', None)
    return jsonify({"success": True})

# ==================== ROTAS OAUTH (SEM PREFIXO /api) ====================

@oauth_bp.route('/login/google')
def login_google():
    """
    Inicia o fluxo de autenticação com Google
    
    Redireciona o usuário para a página de login do Google
    
    Returns:
        Redirect para Google OAuth
    """
    if not google:
        return jsonify({'message': 'OAuth não configurado'}), 500
    
    # URL de callback após autenticação
    redirect_uri = url_for('oauth.authorize_google', _external=True)
    print(f"🔐 Iniciando OAuth Google. Callback: {redirect_uri}")
    
    return google.authorize_redirect(redirect_uri)

@oauth_bp.route('/authorize/google')
def authorize_google():
    """
    Callback do OAuth Google
    
    Recebe o código de autorização do Google e cria/atualiza o usuário
    
    Returns:
        Redirect para /pages/home.html com token JWT
    """
    if not google:
        return redirect('/pages/login.html?error=oauth_not_configured')
    
    try:
        # Obter token de acesso do Google
        token_data = google.authorize_access_token()
        user_info = token_data.get('userinfo')
        
        # Se userinfo não vier no token, buscar manualmente
        if not user_info:
            resp = google.get('https://www.googleapis.com/oauth2/v3/userinfo')
            user_info = resp.json()
        
        print(f"✅ OAuth Google bem-sucedido: {user_info.get('email')}")
        
        # Criar ou atualizar usuário
        user = AuthService.create_or_update_oauth_user(
            email=user_info['email'],
            name=user_info.get('name'),
            picture=user_info.get('picture')
        )
        
        if not user:
            print("❌ Erro ao criar/atualizar usuário OAuth")
            return redirect('/pages/login.html?error=oauth_user_creation_failed')
        
        # Gerar token JWT (NÃO usar session para autenticação)
        token = AuthService.generate_token(user)
        
        # Redirecionar para home com token JWT nos parâmetros
        params = urllib.parse.urlencode({
            'login_success': 'true',
            'token': token,
            'user': json.dumps(user.to_dict())
        })
        
        print(f"✅ Redirecionando para home com token JWT")
        return redirect(f"/pages/home.html?{params}")
        
    except Exception as e:
        print(f"❌ Erro no OAuth: {e}")
        import traceback
        traceback.print_exc()
        
        error_msg = urllib.parse.quote(str(e))
        return redirect(f'/pages/login.html?error=oauth_failed&details={error_msg}')
