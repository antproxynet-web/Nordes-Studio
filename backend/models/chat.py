from extensions import db
from datetime import datetime, timezone

class Message(db.Model):
    __tablename__ = 'message'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.String(50), nullable=True) # image, video, pdf, file
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'timestamp': self.timestamp.isoformat(),
            'is_read': self.is_read
        }

class UserStatus(db.Model):
    __tablename__ = 'user_status'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref=db.backref('status', uselist=False))

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat()
        }
