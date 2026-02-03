from create_app import create_app
from extensions import db
from sqlalchemy import text

def fix_sqlite():
    app = create_app()
    with app.app_context():
        try:
            # SQLite não suporta IF NOT EXISTS em ADD COLUMN diretamente via SQLAlchemy text de forma portável
            # Vamos tentar adicionar e ignorar se já existir
            print("📝 Tentando adicionar colunas ao SQLite...")
            
            try:
                db.session.execute(text("ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT 0 NOT NULL"))
                print("✅ Coluna is_verified adicionada.")
            except Exception as e:
                print(f"ℹ️ Coluna is_verified provavelmente já existe: {e}")
                
            try:
                db.session.execute(text("ALTER TABLE user ADD COLUMN verified_at DATETIME NULL"))
                print("✅ Coluna verified_at adicionada.")
            except Exception as e:
                print(f"ℹ️ Coluna verified_at provavelmente já existe: {e}")
            
            db.session.commit()
            print("✨ Processo concluído.")
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            db.session.rollback()

if __name__ == '__main__':
    fix_sqlite()
