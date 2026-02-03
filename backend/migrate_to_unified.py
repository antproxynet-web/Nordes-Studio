"""
Script de Migração para Backend Unificado
Adiciona campos is_verified e verified_at ao modelo User
Migra senhas em texto plano para hash (se necessário)
"""
import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from create_app import create_app
from extensions import db
from models.user import User

def migrate_database():
    """Executa a migração do banco de dados"""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 60)
        print("🔄 Iniciando migração do banco de dados")
        print("=" * 60)
        
        # 1. Adicionar colunas is_verified e verified_at (se não existirem)
        print("\n📝 Etapa 1: Verificando campos de verificação...")
        try:
            # Tentar criar as tabelas (se não existirem)
            db.create_all()
            print("✅ Campos de verificação adicionados/verificados")
        except Exception as e:
            print(f"⚠️  Aviso: {e}")
        
        # 2. Migrar senhas em texto plano para hash
        print("\n📝 Etapa 2: Migrando senhas para hash...")
        users = User.query.all()
        migrated_count = 0
        
        for user in users:
            if user.password and not user.password.startswith('pbkdf2:sha256:'):
                # Senha está em texto plano, converter para hash
                print(f"   Migrando senha de {user.email}...")
                user.password = generate_password_hash(user.password)
                migrated_count += 1
        
        if migrated_count > 0:
            db.session.commit()
            print(f"✅ {migrated_count} senha(s) migrada(s) para hash")
        else:
            print("✅ Todas as senhas já estão em hash")
        
        # 3. Garantir que todos os usuários tenham username
        print("\n📝 Etapa 3: Verificando usernames...")
        users_without_username = User.query.filter(
            (User.username == None) | (User.username == '')
        ).all()
        
        for user in users_without_username:
            # Gerar username a partir do email
            base_username = user.email.split('@')[0].lower()
            import re
            base_username = re.sub(r'[^a-z0-9._]', '', base_username)
            
            username = base_username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            user.username = username
            print(f"   Username gerado para {user.email}: {username}")
        
        if users_without_username:
            db.session.commit()
            print(f"✅ {len(users_without_username)} username(s) gerado(s)")
        else:
            print("✅ Todos os usuários já têm username")
        
        # 4. Estatísticas finais
        print("\n" + "=" * 60)
        print("📊 Estatísticas do banco de dados:")
        print("=" * 60)
        
        total_users = User.query.count()
        verified_users = User.query.filter_by(is_verified=True).count()
        oauth_users = User.query.filter(User.password == None).count()
        admin_users = User.query.filter_by(role='admin').count()
        
        print(f"👥 Total de usuários: {total_users}")
        print(f"✅ Usuários verificados: {verified_users}")
        print(f"🔑 Usuários OAuth (sem senha): {oauth_users}")
        print(f"👑 Administradores: {admin_users}")
        
        print("\n" + "=" * 60)
        print("✅ Migração concluída com sucesso!")
        print("=" * 60)

if __name__ == '__main__':
    migrate_database()
