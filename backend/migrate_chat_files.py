from create_app import create_app
from extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            print("📝 Adicionando colunas de arquivo à tabela message...")
            
            # Permitir content ser nulo (para mensagens que são apenas arquivos)
            try:
                # SQLite não suporta ALTER COLUMN facilmente, mas vamos tentar adicionar as novas
                db.session.execute(text("ALTER TABLE message ADD COLUMN file_url VARCHAR(255) NULL"))
                print("✅ Coluna file_url adicionada.")
            except Exception as e:
                print(f"ℹ️ file_url já existe ou erro: {e}")
                
            try:
                db.session.execute(text("ALTER TABLE message ADD COLUMN file_type VARCHAR(50) NULL"))
                print("✅ Coluna file_type adicionada.")
            except Exception as e:
                print(f"ℹ️ file_type já existe ou erro: {e}")
            
            db.session.commit()
            print("✨ Migração concluída.")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate()
