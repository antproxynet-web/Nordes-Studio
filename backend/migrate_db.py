import sqlite3
import os

db_path = 'instance/nordes_studio.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Adicionar username se não existir
    if 'username' not in columns:
        print("Adicionando coluna 'username'...")
        cursor.execute("ALTER TABLE user ADD COLUMN username VARCHAR(100)")
        cursor.execute("CREATE UNIQUE INDEX ix_user_username ON user (username)")
    
    # Adicionar is_online se não existir
    if 'is_online' not in columns:
        print("Adicionando coluna 'is_online'...")
        cursor.execute("ALTER TABLE user ADD COLUMN is_online BOOLEAN DEFAULT 0")
    
    # Adicionar last_seen se não existir
    if 'last_seen' not in columns:
        print("Adicionando coluna 'last_seen'...")
        cursor.execute("ALTER TABLE user ADD COLUMN last_seen DATETIME")
        
    # Garantir que todos os usuários tenham um username
    cursor.execute("SELECT id, email, username FROM user")
    users = cursor.fetchall()
    for user_id, email, username in users:
        if not username:
            new_username = email.split('@')[0].lower()
            # Garantir unicidade simples
            cursor.execute("UPDATE user SET username = ? WHERE id = ?", (new_username, user_id))
            print(f"Username gerado para {email}: {new_username}")

    conn.commit()
    conn.close()
    print("Migração concluída com sucesso!")
else:
    print("Banco de dados não encontrado.")
