from app_refactored import create_app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Criar usuário de teste
    if not User.query.filter_by(email='test@manus.im').first():
        user = User(
            email='test@manus.im',
            password=generate_password_hash('test1234'),
            username='testuser',
            name='Usuário Teste',
            role='user'
        )
        db.session.add(user)
        
    # Criar outro usuário para testar o chat
    if not User.query.filter_by(email='nordes@studio.com').first():
        nordes = User(
            email='nordes@studio.com',
            password=generate_password_hash('nordes1234'),
            username='nordes_studio',
            name='Nordes Studio',
            role='admin'
        )
        db.session.add(nordes)
        
    db.session.commit()
    print("Usuários de teste criados com sucesso!")
