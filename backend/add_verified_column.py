"""
Script de migração para adicionar coluna is_verified
Executa ALTER TABLE se a coluna não existir
"""
from create_app import create_app
from extensions import db
from sqlalchemy import text

def add_verified_column():
    """Adiciona coluna is_verified se não existir"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar se a coluna já existe
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name='user' 
                AND column_name='is_verified'
            """))
            
            exists = result.scalar() > 0
            
            if exists:
                print("✅ Coluna is_verified já existe!")
                return
            
            # Adicionar coluna is_verified
            print("📝 Adicionando coluna is_verified...")
            db.session.execute(text("""
                ALTER TABLE user 
                ADD COLUMN is_verified BOOLEAN DEFAULT FALSE NOT NULL
            """))
            
            # Adicionar coluna verified_at
            print("📝 Adicionando coluna verified_at...")
            db.session.execute(text("""
                ALTER TABLE user 
                ADD COLUMN verified_at DATETIME NULL
            """))
            
            db.session.commit()
            print("✅ Colunas adicionadas com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_verified_column()
