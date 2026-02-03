import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'nordes_studio.db')

def update_db():
    if not os.path.exists(db_path):
        print("Banco de dados não encontrado.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela message
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY(sender_id) REFERENCES user(id),
            FOREIGN KEY(receiver_id) REFERENCES user(id)
        )
    ''')
    
    # Criar tabela user_status
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_status (
            user_id INTEGER PRIMARY KEY,
            is_online BOOLEAN DEFAULT 0,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES user(id)
        )
    ''')
    
    # Adicionar coluna username à tabela user se não existir
    try:
        cursor.execute('ALTER TABLE user ADD COLUMN username VARCHAR(100)')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
        
    # Adicionar coluna password à tabela user se não existir
    try:
        cursor.execute('ALTER TABLE user ADD COLUMN password VARCHAR(255)')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass
        
    # Adicionar coluna phone à tabela user se não existir
    try:
        cursor.execute('ALTER TABLE user ADD COLUMN phone VARCHAR(20)')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass

    # Adicionar coluna bio à tabela user se não existir
    try:
        cursor.execute('ALTER TABLE user ADD COLUMN bio TEXT')
    except sqlite3.OperationalError:
        # Coluna já existe
        pass

    # Atualizar usernames nulos
    cursor.execute('SELECT id, email FROM user WHERE username IS NULL')
    users = cursor.fetchall()
    for user_id, email in users:
        username = email.split('@')[0]
        cursor.execute('UPDATE user SET username = ? WHERE id = ?', (username, user_id))
    
    conn.commit()
    conn.close()
    print("Banco de dados atualizado com sucesso!")

if __name__ == '__main__':
    update_db()
