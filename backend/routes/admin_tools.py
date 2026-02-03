from flask import Blueprint, request, jsonify
from extensions import db
from models.user import User
from models.notifications import Notification, HomeLayout
from utils.decorators import token_required, admin_required
import json

admin_bp = Blueprint('admin_tools', __name__, url_prefix='/api/admin')
admin_tools_bp = admin_bp  # Alias para compatibilidade

# --- NOTIFICAÇÕES ---

@admin_tools_bp.route('/notifications/global', methods=['POST'])
@token_required
@admin_required
def send_global_notification(current_user):
    data = request.json
    title = data.get('title')
    message = data.get('message')
    ntype = data.get('type', 'info')
    link = data.get('link')
    
    if not title or not message:
        return jsonify({'message': 'Título e mensagem são obrigatórios'}), 400
        
    # Notificação global (user_id=None)
    new_notif = Notification(
        user_id=None,
        title=title,
        message=message,
        type=ntype,
        link=link
    )
    db.session.add(new_notif)
    db.session.commit()
    
    return jsonify({'message': 'Notificação global enviada com sucesso!'}), 201

@admin_tools_bp.route('/notifications/user/<int:user_id>', methods=['POST'])
@token_required
@admin_required
def send_user_notification(current_user, user_id):
    data = request.json
    title = data.get('title')
    message = data.get('message')
    ntype = data.get('type', 'info')
    
    new_notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=ntype
    )
    db.session.add(new_notif)
    db.session.commit()
    
    return jsonify({'message': 'Notificação enviada ao usuário!'}), 201

# --- HOME LAYOUT ---

@admin_tools_bp.route('/home/layout', methods=['GET'])
def get_home_layout():
    layouts = HomeLayout.query.order_by(HomeLayout.order.asc()).all()
    return jsonify([l.to_dict() for l in layouts])

@admin_tools_bp.route('/home/layout', methods=['POST'])
@token_required
@admin_required
def update_home_layout(current_user):
    data = request.json # Lista de seções [{id, order, is_visible}]
    for item in data:
        layout = HomeLayout.query.get(item['id'])
        if layout:
            layout.order = item.get('order', layout.order)
            layout.is_visible = item.get('is_visible', layout.is_visible)
            if 'config' in item:
                layout.config = json.dumps(item['config'])
    
    db.session.commit()
    return jsonify({'message': 'Layout da Home atualizado!'})

# --- USER NOTIFICATIONS (PUBLIC) ---

@admin_tools_bp.route('/my-notifications', methods=['GET'])
@token_required
def get_my_notifications(current_user):
    # Pega globais + específicas do usuário
    notifications = Notification.query.filter(
        (Notification.user_id == current_user.id) | (Notification.user_id == None)
    ).order_by(Notification.timestamp.desc()).all()
    
    return jsonify([n.to_dict() for n in notifications])

@admin_tools_bp.route('/notifications/read-all', methods=['POST'])
@token_required
def mark_all_read(current_user):
    notifs = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return jsonify({'message': 'Todas marcadas como lidas'})

# --- VERIFICAÇÃO DE USUÁRIOS ---

@admin_tools_bp.route('/verify-user/<int:user_id>', methods=['POST'])
@token_required
@admin_required
def verify_user(current_user, user_id):
    """
    Marca um usuário como verificado
    
    Args:
        user_id: ID do usuário a ser verificado
    
    Returns:
        200: {message, user}
        404: {message} - Usuário não encontrado
    """
    from datetime import datetime, timezone
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    if user.is_verified:
        return jsonify({'message': 'Usuário já está verificado'}), 400
    
    user.is_verified = True
    user.verified_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({
        'message': f'Usuário {user.username or user.email} verificado com sucesso!',
        'user': user.to_dict()
    })

@admin_tools_bp.route('/unverify-user/<int:user_id>', methods=['POST'])
@token_required
@admin_required
def unverify_user(current_user, user_id):
    """
    Remove a verificação de um usuário
    
    Args:
        user_id: ID do usuário
    
    Returns:
        200: {message, user}
        404: {message} - Usuário não encontrado
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    if not user.is_verified:
        return jsonify({'message': 'Usuário não está verificado'}), 400
    
    user.is_verified = False
    user.verified_at = None
    db.session.commit()
    
    return jsonify({
        'message': f'Verificação removida de {user.username or user.email}',
        'user': user.to_dict()
    })

@admin_tools_bp.route('/verified-users', methods=['GET'])
@token_required
@admin_required
def get_verified_users(current_user):
    """
    Lista todos os usuários verificados
    
    Returns:
        200: Lista de usuários verificados
    """
    verified_users = User.query.filter_by(is_verified=True).all()
    return jsonify([user.to_dict() for user in verified_users])

@admin_tools_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    """
    Lista todos os usuários do sistema
    
    Query params:
        search: Buscar por nome, email ou username
        role: Filtrar por role (user, professional, admin)
        verified: Filtrar por verificação (true/false)
    
    Returns:
        200: Lista de usuários
    """
    query = User.query
    
    # Filtro de busca
    search = request.args.get('search')
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            (User.name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern)) |
            (User.username.ilike(search_pattern))
        )
    
    # Filtro de role
    role = request.args.get('role')
    if role:
        query = query.filter_by(role=role)
    
    # Filtro de verificação
    verified = request.args.get('verified')
    if verified is not None:
        is_verified = verified.lower() == 'true'
        query = query.filter_by(is_verified=is_verified)
    
    users = query.all()
    return jsonify([user.to_dict() for user in users])
