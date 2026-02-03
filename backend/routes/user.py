"""
Rotas de Usuário - VERSÃO CORRIGIDA
Correções implementadas:
- Whitelist de campos permitidos no update
- Email não pode ser alterado via PUT
- Validação de ownership
- Melhor tratamento de erros
"""
from flask import Blueprint, request, jsonify
from utils.decorators import token_required
from services.user_service import UserService
from models.config import Config

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Retorna o perfil do usuário autenticado"""
    return jsonify(current_user.to_dict())

@user_bp.route('/check-username', methods=['GET'])
@token_required
def check_username(current_user):
    """Verifica se um username está disponível e segue as regras"""
    username = request.args.get('username', '').strip().lower()
    
    # Validar formato
    is_valid, error = UserService.validate_username(username)
    if not is_valid:
        return jsonify({'available': False, 'message': error})
    
    # Se for o próprio username do usuário, está disponível
    if current_user.username and username == current_user.username.lower():
        return jsonify({'available': True})
    
    from models.user import User
    existing_user = User.query.filter_by(username=username).first()
    
    if existing_user:
        return jsonify({'available': False, 'message': 'Este nome de usuário já está em uso'})
        
    return jsonify({'available': True})

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    Atualiza o perfil do usuário autenticado
    
    ✅ CORREÇÃO: Whitelist de campos permitidos
    ✅ CORREÇÃO: Email NÃO pode ser alterado
    ✅ CORREÇÃO: Validação de ownership (token pertence ao usuário)
    """
    data = request.json
    
    # ✅ WHITELIST: Apenas campos permitidos
    allowed_fields = {'name', 'username', 'bio'}
    
    # Filtrar apenas campos permitidos
    update_data = {}
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]
    
    # ✅ SEGURANÇA: Ignorar email mesmo se enviado
    # O email NUNCA pode ser alterado via este endpoint
    
    # ✅ OWNERSHIP: O token já garante que é o usuário correto
    # (decorador @token_required já valida isso)
    
    # Atualizar perfil
    user, error = UserService.update_profile(
        user_id=current_user.id,
        name=update_data.get('name'),
        username=update_data.get('username'),
        bio=update_data.get('bio'),
        email=None  # ✅ NUNCA aceitar email
    )
    
    if error:
        status_code = 404 if 'não encontrado' in error else 400
        return jsonify({'message': error}), status_code
    
    return jsonify({
        'message': 'Perfil atualizado com sucesso',
        'user': user.to_dict()
    })

@user_bp.route('/profile-picture', methods=['POST'])
@token_required
def upload_profile_picture(current_user):
    """
    Atualiza a foto de perfil do usuário
    
    ✅ CORREÇÃO: Validação de ownership
    ✅ CORREÇÃO: Retorno padronizado de URL
    """
    if 'profile_picture' not in request.files:
        return jsonify({'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        return jsonify({'message': 'Nenhum arquivo selecionado'}), 400
    
    # Validar tamanho (5MB)
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 5 * 1024 * 1024:
        return jsonify({'message': 'Arquivo muito grande. Máximo: 5MB'}), 400
    
    # ✅ OWNERSHIP: O token já garante que é o usuário correto
    # Atualizar foto
    picture_url, error = UserService.update_profile_picture(current_user.id, file)
    
    if error:
        return jsonify({'message': error}), 400
    
    # ✅ CORREÇÃO: Retornar URL padronizada
    return jsonify({
        'message': 'Foto de perfil atualizada com sucesso',
        'picture': picture_url  # Já vem no formato /uploads/filename
    })

# Rota de verificação de senha (para admin)
@user_bp.route('/auth/verify', methods=['POST'])
def verify_password():
    """Verifica a senha de admin"""
    data = request.json
    password = data.get('password')
    
    stored_password = Config.get_value('admin_password', '232341')
    
    if password == stored_password:
        return jsonify({"success": True})
    
    return jsonify({"success": False}), 401
