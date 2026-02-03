from app_refactored import create_app
from extensions import db
from models.user import User
from models.chat import Message, UserStatus
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()
with app.app_context():
    # 1. Criar Usuário A (João)
    user_a = User.query.filter_by(email='joao@teste.com').first()
    if not user_a:
        user_a = User(
            email='joao@teste.com',
            password=generate_password_hash('senha123'),
            username='joao_silva',
            name='João Silva',
            role='user'
        )
        db.session.add(user_a)
        db.session.flush()

    # 2. Criar Usuário B (Maria)
    user_b = User.query.filter_by(email='maria@teste.com').first()
    if not user_b:
        user_b = User(
            email='maria@teste.com',
            password=generate_password_hash('senha123'),
            username='maria_oliveira',
            name='Maria Oliveira',
            role='user'
        )
        db.session.add(user_b)
        db.session.flush()

    db.session.commit()

    # 3. Simular João enviando mensagem para Maria
    msg1 = Message(
        sender_id=user_a.id,
        receiver_id=user_b.id,
        content='Olá Maria, tudo bem?',
        timestamp=datetime.utcnow(),
        is_read=False
    )
    db.session.add(msg1)
    
    # 4. Simular Maria visualizando e respondendo
    msg1.is_read = True # Maria leu
    
    msg2 = Message(
        sender_id=user_b.id,
        receiver_id=user_a.id,
        content='Oi João! Tudo ótimo por aqui, e com você?',
        timestamp=datetime.utcnow(),
        is_read=False
    )
    db.session.add(msg2)
    
    db.session.commit()
    
    print(f"Fluxo de teste concluído!")
    print(f"Usuário A (ID {user_a.id}): {user_a.name} (@{user_a.username})")
    print(f"Usuário B (ID {user_b.id}): {user_b.name} (@{user_b.username})")
    print(f"Mensagem de João: '{msg1.content}' (Status: {'Lida' if msg1.is_read else 'Não lida'})")
    print(f"Resposta de Maria: '{msg2.content}' (Status: {'Lida' if msg2.is_read else 'Não lida'})")
