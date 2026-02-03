from extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # NULL significa global
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info') # info, warning, success, promo
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'timestamp': self.timestamp.isoformat(),
            'is_read': self.is_read,
            'link': self.link
        }

class HomeLayout(db.Model):
    __tablename__ = 'home_layout'
    
    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)
    config = db.Column(db.Text, nullable=True) # JSON com configurações extras

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'section_name': self.section_name,
            'order': self.order,
            'is_visible': self.is_visible,
            'config': json.loads(self.config) if self.config else {}
        }
