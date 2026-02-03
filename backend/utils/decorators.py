"""
Decorators para autenticação e autorização
"""
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from models.user import User

def token_required(f):
    """
    Decorator para rotas que requerem autenticação via JWT
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar token no header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token ausente!'}), 401
        
        try:
            # Decodificar token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'message': 'Usuário inválido!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
        except Exception as e:
            return jsonify({'message': f'Erro ao validar token: {str(e)}'}), 401
        
        # Passar o usuário atual para a função decorada
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """
    Decorator para rotas que requerem privilégios de administrador
    Deve ser usado após @token_required
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        # Verificar se é admin e se é o email autorizado
        admin_email = current_app.config.get('ADMIN_EMAIL', 'ant.proxy.net@gmail.com')
        
        if current_user.role != 'admin' or current_user.email != admin_email:
            return jsonify({'message': 'Acesso restrito ao administrador!'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def professional_required(f):
    """
    Decorator para rotas que requerem privilégios de profissional
    Deve ser usado após @token_required
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role not in ['professional', 'admin']:
            return jsonify({'message': 'Acesso restrito a profissionais!'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated
