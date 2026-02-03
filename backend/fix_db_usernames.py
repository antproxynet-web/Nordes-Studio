import os
import re
from app_refactored import app
from extensions import db
from models.user import User

def validate_username(username):
    if not username:
        return False
    if not re.match(r'^[a-z0-9._]+$', username):
        return False
    return True

def fix_usernames():
    with app.app_context():
        print("Iniciando correção de usernames...")
        users = User.query.all()
        usernames_seen = set()
        
        for user in users:
            original_username = user.username
            
            # 1. Converter para minúsculas e remover espaços
            new_username = (user.username or user.email.split('@')[0]).strip().lower()
            
            # 2. Remover caracteres inválidos
            new_username = re.sub(r'[^a-z0-9._]', '', new_username)
            
            # 3. Garantir tamanho mínimo
            if len(new_username) < 3:
                new_username = (new_username + "user")[:10]
            
            # 4. Garantir unicidade
            base_username = new_username
            counter = 1
            while new_username in usernames_seen:
                new_username = f"{base_username}{counter}"
                counter += 1
            
            usernames_seen.add(new_username)
            
            if user.username != new_username:
                print(f"Atualizando usuário {user.id}: {original_username} -> {new_username}")
                user.username = new_username
        
        try:
            db.session.commit()
            print("Usernames corrigidos com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar alterações: {e}")

if __name__ == "__main__":
    fix_usernames()
