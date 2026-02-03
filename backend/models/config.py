"""
Model de Configuração
"""
from extensions import db

class Config(db.Model):
    """Modelo de configurações do sistema"""
    
    __tablename__ = 'config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    value = db.Column(db.String(255), nullable=False)
    
    def to_dict(self):
        """Converte a configuração para dicionário"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }
    
    @staticmethod
    def get_value(key, default=None):
        """Busca um valor de configuração"""
        config = Config.query.filter_by(key=key).first()
        return config.value if config else default
    
    @staticmethod
    def set_value(key, value):
        """Define um valor de configuração"""
        config = Config.query.filter_by(key=key).first()
        if config:
            config.value = value
        else:
            config = Config(key=key, value=value)
            db.session.add(config)
        db.session.commit()
        return config
    
    def __repr__(self):
        return f'<Config {self.key}={self.value}>'
