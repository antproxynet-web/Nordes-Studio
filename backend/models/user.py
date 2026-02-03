"""
Model de Usuário - VERSÃO CORRIGIDA

Correções implementadas:
- Normalização de URL de foto de perfil no to_dict
- Melhor estrutura de dados
"""
from extensions import db

class User(db.Model):
    """Modelo de usuário do sistema"""
    
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255))  # Hash da senha
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, index=True)
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    picture = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')  # user, professional, admin
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=db.func.now())
    
    # Sistema de verificação
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self, include_sensitive=False):
        """
        Converte o usuário para dicionário
        
        ✅ CORREÇÃO: Normaliza URL de foto de perfil
        """
        # ✅ CORREÇÃO: Normalizar URL da foto
        picture_url = self._normalize_picture_url(self.picture)
        
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'username': self.username,
            'phone': self.phone,
            'bio': self.bio,
            'picture': picture_url,  # ✅ URL normalizada
            'role': self.role,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_verified': self.is_verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None
        }
        
        if include_sensitive:
            data['password'] = self.password
        
        return data
    
    def _normalize_picture_url(self, picture):
        """
        ✅ NOVO: Normaliza URL de foto de perfil
        
        Args:
            picture: URL ou nome do arquivo
        
        Returns:
            str: URL normalizada ou None
        """
        if not picture:
            return None
        
        # Se já é URL completa (OAuth - Google, Facebook, etc.)
        if picture.startswith('http://') or picture.startswith('https://'):
            return picture
        
        # Se já começa com /uploads/
        if picture.startswith('/uploads/'):
            return picture
        
        # Caso contrário, adicionar /uploads/
        return f'/uploads/{picture}'
    
    def __repr__(self):
        return f'<User {self.email}>'
