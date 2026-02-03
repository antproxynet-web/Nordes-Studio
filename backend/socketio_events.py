"""
Eventos SocketIO para chat em tempo real
Gerencia conexões, mensagens e status de usuários
"""
import jwt
from flask import request
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timezone
from extensions import db
from models.user import User
from models.chat import Message

# Dicionário de usuários online: {user_id: sid}
online_users = {}

def register_events(socketio, app):
    """
    Registra todos os eventos SocketIO
    
    Args:
        socketio: Instância do SocketIO
        app: Aplicação Flask
    """
    
    @socketio.on('connect')
    def handle_connect():
        """
        Evento de conexão do cliente
        
        Valida o token JWT e registra o usuário como online
        """
        token = request.args.get('token')
        if not token:
            print("❌ Conexão rejeitada: Token ausente")
            return False  # Rejeitar conexão
        
        try:
            with app.app_context():
                # Decodificar token JWT
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                user_id = data['user_id']
                
                # Registrar usuário online
                online_users[user_id] = request.sid
                
                # Atualizar status no banco
                user = User.query.get(user_id)
                if user:
                    user.is_online = True
                    user.last_seen = datetime.now(timezone.utc)
                    db.session.commit()
                
                # Entrar na sala do usuário
                join_room(f"user_{user_id}")
                
                # Notificar todos que o usuário está online
                emit('user_status', {
                    'user_id': user_id, 
                    'status': 'online'
                }, broadcast=True)
                
                print(f"✅ Usuário {user_id} conectado via WebSocket (SID: {request.sid})")
                
        except jwt.ExpiredSignatureError:
            print("❌ Conexão rejeitada: Token expirado")
            return False
        except jwt.InvalidTokenError:
            print("❌ Conexão rejeitada: Token inválido")
            return False
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """
        Evento de desconexão do cliente
        
        Atualiza o status do usuário para offline
        """
        user_id = None
        
        # Encontrar usuário pelo SID
        for uid, sid in online_users.items():
            if sid == request.sid:
                user_id = uid
                break
        
        if user_id:
            with app.app_context():
                # Remover do dicionário de usuários online
                del online_users[user_id]
                
                # Atualizar status no banco
                user = User.query.get(user_id)
                if user:
                    user.is_online = False
                    user.last_seen = datetime.now(timezone.utc)
                    db.session.commit()
                
                # Notificar todos que o usuário está offline
                emit('user_status', {
                    'user_id': user_id, 
                    'status': 'offline'
                }, broadcast=True)
                
                print(f"🔴 Usuário {user_id} desconectado")
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """
        Evento de envio de mensagem
        
        Salva a mensagem no banco e envia para o destinatário
        
        Args:
            data: {receiver_id: int, content: str}
        """
        sender_sid = request.sid
        sender_id = None
        
        # Encontrar ID do remetente
        for uid, sid in online_users.items():
            if sid == sender_sid:
                sender_id = uid
                break
        
        if not sender_id:
            print("❌ Mensagem rejeitada: Usuário não autenticado")
            return
        
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        
        if not receiver_id or not content:
            print("❌ Mensagem rejeitada: Dados incompletos")
            return
        
        with app.app_context():
            try:
                # Salvar mensagem no banco
                new_msg = Message(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    content=content
                )
                db.session.add(new_msg)
                db.session.commit()
                
                msg_dict = new_msg.to_dict()
                
                # Enviar para o destinatário se estiver online
                emit('new_message', msg_dict, room=f"user_{receiver_id}")
                
                # Confirmar para o remetente
                emit('message_sent', msg_dict)
                
                print(f"📨 Mensagem enviada: {sender_id} -> {receiver_id}")
                
            except Exception as e:
                print(f"❌ Erro ao enviar mensagem: {e}")
                emit('message_error', {'message': 'Erro ao enviar mensagem'})
    
    @socketio.on('mark_read')
    def handle_mark_read(data):
        """
        Evento de marcação de mensagem como lida
        
        Args:
            data: {message_id: int}
        """
        message_id = data.get('message_id')
        
        if not message_id:
            return
        
        with app.app_context():
            try:
                msg = Message.query.get(message_id)
                if msg:
                    msg.is_read = True
                    db.session.commit()
                    
                    # Notificar o remetente que a mensagem foi lida
                    emit('message_read', {
                        'message_id': message_id
                    }, room=f"user_{msg.sender_id}")
                    
                    print(f"✓ Mensagem {message_id} marcada como lida")
                    
            except Exception as e:
                print(f"❌ Erro ao marcar mensagem como lida: {e}")
    
    @socketio.on('typing')
    def handle_typing(data):
        """
        Evento de digitação (opcional)
        
        Notifica o destinatário que o remetente está digitando
        
        Args:
            data: {receiver_id: int, is_typing: bool}
        """
        sender_sid = request.sid
        sender_id = None
        
        for uid, sid in online_users.items():
            if sid == sender_sid:
                sender_id = uid
                break
        
        if not sender_id:
            return
        
        receiver_id = data.get('receiver_id')
        is_typing = data.get('is_typing', False)
        
        if receiver_id:
            emit('user_typing', {
                'user_id': sender_id,
                'is_typing': is_typing
            }, room=f"user_{receiver_id}")
