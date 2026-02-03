from app_refactored import create_app
from flask_jwt_extended import create_access_token
from models.user import User

app = create_app()
with app.app_context():
    # Buscar o usuário João
    user = User.query.filter_by(email='joao@teste.com').first()
    if user:
        token = create_access_token(identity=user.id)
        print(f"Token para João (ID {user.id}):")
        print(token)
    else:
        print("Usuário não encontrado")
