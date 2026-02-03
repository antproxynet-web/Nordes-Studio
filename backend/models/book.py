"""
Model de Livro
"""
from extensions import db

class Book(db.Model):
    """Modelo de livro/mangá do sistema"""
    
    __tablename__ = 'book'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    release_date = db.Column(db.String(50), nullable=True)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), nullable=True, index=True)
    
    def to_dict(self):
        """Converte o livro para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'price': self.price,
            'description': self.description,
            'image': self.image_url,
            'release_date': self.release_date,
            'stock': self.stock,
            'category': self.category
        }
    
    def __repr__(self):
        return f'<Book {self.title}>'
