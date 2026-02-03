import sqlite3
import os

db_path = 'instance/nordes_studio.db'

if os.path.exists(db_path):
    print(f"Conectando ao banco: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adicionando coluna is_verified...")
        cursor.execute("ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError as e:
        print(f"Aviso: {e}")
        
    try:
        print("Adicionando coluna verified_at...")
        cursor.execute("ALTER TABLE user ADD COLUMN verified_at DATETIME")
    except sqlite3.OperationalError as e:
        print(f"Aviso: {e}")
        
    conn.commit()
    conn.close()
    print("Migração manual concluída.")
else:
    print("Banco de dados não encontrado para migração manual.")
