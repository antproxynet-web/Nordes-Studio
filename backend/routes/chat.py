from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models.user import User
from models.chat import Message, UserStatus
from utils.decorators import token_required
from datetime import datetime, timezone
import os
import uuid
from werkzeug.utils import secure_filename

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    search = request.args.get('search', '')
    query = User.query.filter(User.id != current_user.id)
    
    if search:
        # ✅ Busca otimizada por username (estilo Instagram)
        search_pattern = f'%{search}%'
        query = query.filter(
            (User.username.ilike(search_pattern)) | 
            (User.name.ilike(search_pattern))
        )
    
    users = query.limit(20).all()
    result = []
    for user in users:
        # ✅ O to_dict() já inclui is_online e last_seen atualizados
        user_data = user.to_dict()
        
        # Última mensagem para a lista de conversas
        last_msg = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == user.id)) |
            ((Message.sender_id == user.id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.timestamp.desc()).first()
        
        user_data['last_message'] = last_msg.content if last_msg else ""
        user_data['last_message_time'] = last_msg.timestamp.isoformat() if last_msg else None
        
        # Contagem de mensagens não lidas
        unread_count = Message.query.filter_by(sender_id=user.id, receiver_id=current_user.id, is_read=False).count()
        user_data['unread_count'] = unread_count
        
        result.append(user_data)
        
    return jsonify(result)

@chat_bp.route('/messages/<int:other_user_id>', methods=['GET'])
@token_required
def get_messages(current_user, other_user_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    
    # Marcar como lidas
    unread = Message.query.filter_by(sender_id=other_user_id, receiver_id=current_user.id, is_read=False).all()
    for m in unread:
        m.is_read = True
    db.session.commit()
    
    return jsonify([m.to_dict() for m in messages])

@chat_bp.route('/send', methods=['POST'])
@token_required
def send_message(current_user):
    data = request.json
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not receiver_id or not content:
        return jsonify({'message': 'Dados incompletos'}), 400
        
    new_msg = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
    db.session.add(new_msg)
    db.session.commit()
    
    return jsonify(new_msg.to_dict()), 201

@chat_bp.route('/status', methods=['POST'])
@token_required
def update_status(current_user):
    data = request.json
    is_online = data.get('is_online', True)
    
    status = UserStatus.query.get(current_user.id)
    if not status:
        status = UserStatus(user_id=current_user.id)
        db.session.add(status)
        
    status.is_online = is_online
    status.last_seen = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({'message': 'Status atualizado'})

@chat_bp.route('/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_info(current_user, user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
        
    status = UserStatus.query.get(user.id)
    user_data = user.to_dict()
    user_data['is_online'] = status.is_online if status else False
    user_data['last_seen'] = status.last_seen.isoformat() if status else None
    
    return jsonify(user_data)

@chat_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    receiver_id = request.form.get('receiver_id')
    content = request.form.get('content', '')
    
    if not receiver_id:
        return jsonify({'message': 'Destinatário não informado'}), 400
    
    if file.filename == '':
        return jsonify({'message': 'Nome de arquivo inválido'}), 400
    
    # Configurar pasta de upload
    upload_dir = os.path.join(current_app.root_path, 'uploads', 'chat')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Gerar nome único
    ext = os.path.splitext(file.filename)[1].lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)
    
    file.save(filepath)
    
    # Determinar tipo de arquivo
    file_type = 'file'
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        file_type = 'image'
    elif ext in ['.mp4', '.webm', '.ogg', '.mov']:
        file_type = 'video'
    elif ext == '.pdf':
        file_type = 'pdf'
    
    file_url = f"/uploads/chat/{filename}"
    
    # Salvar mensagem no banco
    new_msg = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content,
        file_url=file_url,
        file_type=file_type
    )
    db.session.add(new_msg)
    db.session.commit()
    
    return jsonify(new_msg.to_dict()), 201
