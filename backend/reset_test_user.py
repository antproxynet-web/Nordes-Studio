from app_new import create_app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash

app, _ = create_app('development')
with app.app_context():
    user = User.query.filter_by(email='test@manus.im').first()
    if user:
        user.password = generate_password_hash('123456')
        db.session.commit()
        print("✓ Senha do usuário test@manus.im resetada para '123456'")
    else:
        print("✗ Usuário test@manus.im não encontrado")
