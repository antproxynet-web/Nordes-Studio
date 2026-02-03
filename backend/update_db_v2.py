import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'nordes_studio.db')

def update_db():
    if not os.path.exists(db_path):
        print("Banco de dados não encontrado.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela notification
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            type VARCHAR(50) DEFAULT 'info',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            link VARCHAR(255),
            FOREIGN KEY(user_id) REFERENCES user(id)
        )
    ''')
    
    # Criar tabela home_layout
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS home_layout (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_name VARCHAR(100) NOT NULL,
            "order" INTEGER DEFAULT 0,
            is_visible BOOLEAN DEFAULT 1,
            config TEXT
        )
    ''')
    
    # Inserir seções padrão se a tabela estiver vazia
    cursor.execute('SELECT COUNT(*) FROM home_layout')
    if cursor.fetchone()[0] == 0:
        sections = [
            ('banner', 0, 1),
            ('icons', 1, 1),
            ('featured', 2, 1),
            ('best_sellers', 3, 1),
            ('newsletter', 4, 1)
        ]
        cursor.executemany('INSERT INTO home_layout (section_name, "order", is_visible) VALUES (?, ?, ?)', sections)
    
    conn.commit()
    conn.close()
    print("Banco de dados atualizado (v2) com sucesso!")

if __name__ == '__main__':
    update_db()
