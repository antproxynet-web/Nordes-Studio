import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'nordes_studio.db')

def create_admin():
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Garantir que a tabela existe (caso o app ainda não tenha rodado)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(120) UNIQUE NOT NULL,
            name VARCHAR(100),
            picture VARCHAR(255),
            role VARCHAR(20) DEFAULT 'user'
        )
    ''')
    
    admin_email = 'ant.proxy.net@gmail.com'
    admin_name = 'Admin God'
    
    # Verificar se já existe
    cursor.execute('SELECT id FROM user WHERE email = ?', (admin_email,))
    user = cursor.fetchone()
    
    if user:
        cursor.execute('UPDATE user SET role = "admin", name = ? WHERE email = ?', (admin_name, admin_email))
        print(f"Usuário {admin_email} atualizado para ADMIN.")
    else:
        cursor.execute('INSERT INTO user (email, name, role) VALUES (?, ?, ?)', (admin_email, admin_name, 'admin'))
        print(f"Usuário {admin_email} criado como ADMIN.")
    
    # Também atualizar a senha do config manager se necessário
    cursor.execute('CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, key VARCHAR(50) UNIQUE, value VARCHAR(255))')
    cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', ('admin_password', 'admingod777'))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_admin()
