"""
Script de Migração de Senhas
Converte senhas em texto plano para hash bcrypt
"""
from werkzeug.security import generate_password_hash, check_password_hash
from app_new import create_app
from models.user import User
from extensions import db

def is_hashed(password):
    """Verifica se a senha já está hasheada (bcrypt)"""
    if not password:
        return True  # Senhas vazias (OAuth) não precisam ser migradas
    
    # Senhas bcrypt começam com $2b$ ou $2a$ ou $2y$
    return password.startswith('$2b$') or password.startswith('$2a$') or password.startswith('$2y$')

def migrate_passwords():
    """Migra todas as senhas em texto plano para hash"""
    app, _ = create_app('development')
    
    with app.app_context():
        users = User.query.all()
        migrated_count = 0
        skipped_count = 0
        
        print("=" * 60)
        print("🔐 Migrando senhas para hash bcrypt")
        print("=" * 60)
        
        for user in users:
            if not user.password:
                print(f"⏭️  {user.email}: Sem senha (OAuth) - ignorado")
                skipped_count += 1
                continue
            
            if is_hashed(user.password):
                print(f"✓ {user.email}: Senha já hasheada - ignorado")
                skipped_count += 1
                continue
            
            # Senha em texto plano - migrar
            old_password = user.password
            user.password = generate_password_hash(old_password)
            migrated_count += 1
            print(f"🔄 {user.email}: Senha migrada com sucesso")
        
        if migrated_count > 0:
            db.session.commit()
            print("=" * 60)
            print(f"✅ Migração concluída!")
            print(f"   - {migrated_count} senha(s) migrada(s)")
            print(f"   - {skipped_count} usuário(s) ignorado(s)")
            print("=" * 60)
        else:
            print("=" * 60)
            print("✓ Nenhuma senha precisou ser migrada")
            print(f"  Total de usuários: {len(users)}")
            print("=" * 60)

if __name__ == '__main__':
    migrate_passwords()
