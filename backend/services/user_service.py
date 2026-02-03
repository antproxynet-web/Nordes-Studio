"""
Serviço de Usuário - VERSÃO CORRIGIDA
Contém toda a lógica de negócio relacionada a usuários

Correções implementadas:
- Email não pode ser alterado via update_profile
- Retorno padronizado de URLs de imagem
- Melhor validação de dados
"""
from extensions import db
from models.user import User
from utils.helpers import save_upload_file, delete_upload_file
import re

class UserService:
    """Serviço de gerenciamento de usuários"""
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Busca um usuário por ID
        
        Args:
            user_id: ID do usuário
        
        Returns:
            User: Objeto do usuário ou None
        """
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        """
        Busca um usuário por email
        
        Args:
            email: Email do usuário
        
        Returns:
            User: Objeto do usuário ou None
        """
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def validate_username(username):
        """
        Valida o formato do username: letras minúsculas, números, ponto e underline
        """
        if not username:
            return False, "Username não pode ser vazio"
        if len(username) < 3:
            return False, "Username muito curto (mínimo 3 caracteres)"
        if len(username) > 30:
            return False, "Username muito longo (máximo 30 caracteres)"
        
        # Regex: apenas letras minúsculas, números, ponto e underline
        if not re.match(r'^[a-z0-9._]+$', username):
            return False, "Username deve conter apenas letras minúsculas, números, ponto (.) e underline (_)"
        
        return True, None

    @staticmethod
    def update_profile(user_id, name=None, username=None, bio=None, email=None):
        """
        Atualiza o perfil do usuário
        
        ✅ CORREÇÃO: Email não pode ser alterado (parâmetro ignorado)
        ✅ CORREÇÃO: Validação mais robusta
        
        Args:
            user_id: ID do usuário
            name: Nome completo (opcional)
            username: Nome de usuário (opcional)
            bio: Biografia (opcional)
            email: Email (IGNORADO - não pode ser alterado)
        
        Returns:
            tuple: (user, error_message)
        """
        user = User.query.get(user_id)
        
        if not user:
            return None, 'Usuário não encontrado'
        
        # Atualizar campos se fornecidos
        if name is not None:
            user.name = name
            
        if username is not None:
            username = username.strip().lower()
            
            # Validar formato
            is_valid, error = UserService.validate_username(username)
            if not is_valid:
                return None, error
                
            # Verificar se username já existe
            existing = User.query.filter_by(username=username).first()
            if existing and existing.id != user_id:
                return None, 'Este nome de usuário já está em uso'
            user.username = username
            
        if bio is not None:
            user.bio = bio
        
        # ✅ SEGURANÇA CRÍTICA: Email NÃO pode ser alterado
        # Mesmo que o parâmetro seja enviado, ele é IGNORADO
        # Para alterar email, deve existir um endpoint específico com:
        # - Verificação de senha atual
        # - Confirmação por email
        # - Rate limiting
        
        try:
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, f'Erro ao atualizar perfil: {str(e)}'
    
    @staticmethod
    def update_profile_picture(user_id, image_file):
        """
        Atualiza a foto de perfil do usuário
        
        ✅ CORREÇÃO: Retorno padronizado de URL
        
        Args:
            user_id: ID do usuário
            image_file: Arquivo de imagem
        
        Returns:
            tuple: (picture_url, error_message)
        """
        user = User.query.get(user_id)
        
        if not user:
            return None, 'Usuário não encontrado'
        
        # Salvar nova imagem
        new_picture = save_upload_file(image_file, prefix=f'profile_{user_id}')
        
        if not new_picture:
            return None, 'Erro ao salvar imagem'
        
        # Remover imagem antiga se existir (apenas se for local)
        if user.picture and user.picture.startswith('/uploads/'):
            old_filename = user.picture.split('/uploads/')[1]
            delete_upload_file(old_filename)
        
        # ✅ CORREÇÃO: Sempre retornar no formato /uploads/filename
        user.picture = f'/uploads/{new_picture}'
        
        try:
            db.session.commit()
            # ✅ CORREÇÃO: Retornar URL padronizada
            return user.picture, None
        except Exception as e:
            db.session.rollback()
            delete_upload_file(new_picture)
            return None, f'Erro ao atualizar foto: {str(e)}'
    
    @staticmethod
    def change_role(user_id, new_role):
        """
        Altera o papel do usuário
        
        Args:
            user_id: ID do usuário
            new_role: Novo papel (user, professional, admin)
        
        Returns:
            tuple: (user, error_message)
        """
        user = User.query.get(user_id)
        
        if not user:
            return None, 'Usuário não encontrado'
        
        if new_role not in ['user', 'professional', 'admin']:
            return None, 'Papel inválido'
        
        user.role = new_role
        
        try:
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, f'Erro ao alterar papel: {str(e)}'
    
    @staticmethod
    def normalize_picture_url(picture):
        """
        ✅ NOVO: Normaliza URL de foto de perfil
        
        Args:
            picture: URL ou nome do arquivo
        
        Returns:
            str: URL normalizada
        """
        if not picture:
            return None
        
        # Se já é URL completa (OAuth)
        if picture.startswith('http://') or picture.startswith('https://'):
            return picture
        
        # Se já começa com /uploads/
        if picture.startswith('/uploads/'):
            return picture
        
        # Caso contrário, adicionar /uploads/
        return f'/uploads/{picture}'
