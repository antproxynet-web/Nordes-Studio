from create_app import create_app
from extensions import db
from models.user import User
from datetime import datetime, timezone

def verify_adm():
    app = create_app()
    with app.app_context():
        email = "ant.proxy.net@gmail.com"
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_verified = True
            user.verified_at = datetime.now(timezone.utc)
            db.session.commit()
            print(f"✅ Usuário {email} verificado com sucesso!")
        else:
            print(f"❌ Usuário {email} não encontrado!")

if __name__ == '__main__':
    verify_adm()
