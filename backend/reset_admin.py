from create_app import create_app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='ant.proxy.net@gmail.com').first()
    if user:
        print(f"Usuário encontrado: {user.email}, Role: {user.role}")
        user.password = generate_password_hash('adminX999')
        user.role = 'admin' # Garantir que é admin
        db.session.commit()
        print("Senha resetada para 'adminX999' e role garantida como 'admin'.")
    else:
        print("Usuário não encontrado. Criando novo admin...")
        new_admin = User(
            email='ant.proxy.net@gmail.com',
            username='admin_test',
            password=generate_password_hash('adminX999'),
            role='admin',
            is_verified=True
        )
        db.session.add(new_admin)
        db.session.commit()
        print("Novo admin criado com sucesso.")
