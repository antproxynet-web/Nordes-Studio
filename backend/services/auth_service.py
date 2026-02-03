"""
Serviço de Autenticação
Contém toda a lógica de negócio relacionada à autenticação
"""
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from extensions import db
from models.user import User

class AuthService:
    """Serviço de autenticação de usuários"""
    
    @staticmethod
    def create_user(email, password, name=None, phone=None, username=None):
        """
        Cria um novo usuário
        
        Args:
            email: Email do usuário
            password: Senha em texto plano
            name: Nome completo (opcional)
            phone: Telefone (opcional)
            username: Nome de usuário único (opcional)
        
        Returns:
            tuple: (user, error_message)
        """
        # Verificar se email já existe
        if User.query.filter_by(email=email).first():
            return None, 'Email já cadastrado'
        
        # Se username foi fornecido, validar
        if username:
            username = username.lower()
            import re
            if not re.match(r'^[a-z0-9._]+$', username):
                return None, 'Username inválido. Use apenas letras, números, . e _'
            
            if User.query.filter_by(username=username).first():
                return None, 'Este nome de usuário já está em uso'
        else:
            # Gerar username base a partir do email
            base_username = email.split('@')[0].lower()
            import re
            base_username = re.sub(r'[^a-z0-9._]', '', base_username)
            
            # Garantir que seja único
            username = base_username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1

        # Hash da senha
        password_hash = generate_password_hash(password)

        # Criar usuário
        user = User(
            email=email,
            password=password_hash,
            name=name,
            username=username,
            phone=phone,
            role='user'
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, f'Erro ao criar usuário: {str(e)}'
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Autentica um usuário
        
        Args:
            email: Email do usuário
            password: Senha em texto plano
        
        Returns:
            tuple: (user, error_message)
        """
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return None, 'Usuário não encontrado'
        
        # Verificar senha
        if not check_password_hash(user.password, password):
            return None, 'Senha incorreta'
        
        return user, None
    
    @staticmethod
    def generate_token(user):
        """
        Gera um token JWT para o usuário
        
        Args:
            user: Objeto User
        
        Returns:
            str: Token JWT
        """
        expiration_hours = current_app.config.get('JWT_EXPIRATION_HOURS', 24)
        
        token = jwt.encode({
            'user_id': int(user.id),
            'exp': datetime.utcnow() + timedelta(hours=expiration_hours)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return token
    
    @staticmethod
    def create_or_update_oauth_user(email, name=None, picture=None):
        """
        Cria ou atualiza um usuário OAuth (Google)
        
        Args:
            email: Email do usuário
            name: Nome completo (opcional)
            picture: URL da foto de perfil (opcional)
        
        Returns:
            User: Objeto do usuário
        """
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Gerar username base
            base_username = email.split('@')[0].lower()
            import re
            base_username = re.sub(r'[^a-z0-9._]', '', base_username)
            
            # Garantir que seja único
            username = base_username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1

            # Criar novo usuário OAuth
            user = User(
                email=email,
                name=name,
                username=username,
                picture=picture,
                role='user'
            )
            db.session.add(user)
        else:
            # Atualizar informações se necessário
            if name and not user.name:
                user.name = name
            if picture and not user.picture:
                user.picture = picture
        
        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar/atualizar usuário OAuth: {e}")
            return None
