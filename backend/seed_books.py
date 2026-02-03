"""
Script de Seed para popular o banco de dados com livros
Utiliza as imagens já existentes na pasta uploads/
"""
import os
import sys
from app import app, db, Book

# Dados dos livros (baseado nas imagens disponíveis)
BOOKS_DATA = [
    # Mangás
    {"title": "One Piece Vol. 1", "author": "Eiichiro Oda", "price": 29.90, "description": "A jornada de Luffy em busca do One Piece começa aqui!", "image_url": "manga1.jpg", "category": "manga", "stock": 50, "release_date": "2024-01-15"},
    {"title": "Naruto Vol. 1", "author": "Masashi Kishimoto", "price": 27.90, "description": "A história do ninja que sonha em ser Hokage.", "image_url": "manga2.jpg", "category": "manga", "stock": 45, "release_date": "2024-01-20"},
    {"title": "Attack on Titan Vol. 1", "author": "Hajime Isayama", "price": 32.90, "description": "A humanidade luta pela sobrevivência contra os titãs.", "image_url": "manga3.jpg", "category": "manga", "stock": 40, "release_date": "2024-02-01"},
    
    # Livros de Fantasia
    {"title": "O Senhor dos Anéis", "author": "J.R.R. Tolkien", "price": 89.90, "description": "A épica jornada para destruir o Um Anel.", "image_url": "livro-1.jpg", "category": "fantasia", "stock": 30, "release_date": "2024-01-10"},
    {"title": "Harry Potter e a Pedra Filosofal", "author": "J.K. Rowling", "price": 45.90, "description": "O início da saga do bruxo mais famoso do mundo.", "image_url": "livro-2.jpg", "category": "fantasia", "stock": 60, "release_date": "2024-01-12"},
    {"title": "As Crônicas de Nárnia", "author": "C.S. Lewis", "price": 67.90, "description": "A aventura mágica além do guarda-roupa.", "image_url": "livro-3.jpg", "category": "fantasia", "stock": 35, "release_date": "2024-01-18"},
    {"title": "O Hobbit", "author": "J.R.R. Tolkien", "price": 54.90, "description": "A jornada de Bilbo Bolseiro.", "image_url": "livro-4.jpg", "category": "fantasia", "stock": 40, "release_date": "2024-02-05"},
    {"title": "Percy Jackson e o Ladrão de Raios", "author": "Rick Riordan", "price": 42.90, "description": "Mitologia grega na era moderna.", "image_url": "livro-5.jpg", "category": "fantasia", "stock": 50, "release_date": "2024-02-10"},
    
    # Livros de Ficção
    {"title": "1984", "author": "George Orwell", "price": 38.90, "description": "Um clássico distópico sobre vigilância e controle.", "image_url": "livro-6.jpg", "category": "ficcao", "stock": 45, "release_date": "2024-01-25"},
    {"title": "O Pequeno Príncipe", "author": "Antoine de Saint-Exupéry", "price": 29.90, "description": "Uma fábula poética sobre amor e amizade.", "image_url": "livro-7.jpg", "category": "ficcao", "stock": 70, "release_date": "2024-01-30"},
    {"title": "A Revolução dos Bichos", "author": "George Orwell", "price": 35.90, "description": "Uma sátira política sobre poder e corrupção.", "image_url": "livro-8.jpg", "category": "ficcao", "stock": 40, "release_date": "2024-02-08"},
    {"title": "O Alquimista", "author": "Paulo Coelho", "price": 39.90, "description": "A busca pela realização dos sonhos.", "image_url": "livro-9.jpg", "category": "ficcao", "stock": 55, "release_date": "2024-02-12"},
    
    # Livros de Terror
    {"title": "It - A Coisa", "author": "Stephen King", "price": 59.90, "description": "O terror que assombra a cidade de Derry.", "image_url": "livro-10.jpg", "category": "terror", "stock": 30, "release_date": "2024-01-22"},
    {"title": "O Iluminado", "author": "Stephen King", "price": 54.90, "description": "Horror psicológico no Hotel Overlook.", "image_url": "livro-11.jpg", "category": "terror", "stock": 35, "release_date": "2024-02-03"},
    {"title": "Drácula", "author": "Bram Stoker", "price": 44.90, "description": "O clássico vampiro da literatura.", "image_url": "livro-12.jpg", "category": "terror", "stock": 40, "release_date": "2024-02-07"},
    {"title": "Frankenstein", "author": "Mary Shelley", "price": 42.90, "description": "A criação que se volta contra o criador.", "image_url": "livro-13.jpg", "category": "terror", "stock": 38, "release_date": "2024-02-14"},
    
    # Mais Livros Diversos
    {"title": "Dom Casmurro", "author": "Machado de Assis", "price": 34.90, "description": "Um clássico da literatura brasileira.", "image_url": "livro-14.jpg", "category": "livro", "stock": 50, "release_date": "2024-01-28"},
    {"title": "Grande Sertão: Veredas", "author": "Guimarães Rosa", "price": 49.90, "description": "Uma obra-prima do regionalismo brasileiro.", "image_url": "livro-15.jpg", "category": "livro", "stock": 25, "release_date": "2024-02-11"},
    {"title": "Memórias Póstumas de Brás Cubas", "author": "Machado de Assis", "price": 36.90, "description": "Narrado por um defunto autor.", "image_url": "livro-16.jpg", "category": "livro", "stock": 45, "release_date": "2024-02-16"},
    {"title": "O Cortiço", "author": "Aluísio Azevedo", "price": 32.90, "description": "Retrato do naturalismo brasileiro.", "image_url": "livro-17.jpg", "category": "livro", "stock": 40, "release_date": "2024-02-18"},
    {"title": "Capitães da Areia", "author": "Jorge Amado", "price": 38.90, "description": "A vida dos meninos de rua em Salvador.", "image_url": "livro-18.jpg", "category": "livro", "stock": 35, "release_date": "2024-02-20"},
    {"title": "Vidas Secas", "author": "Graciliano Ramos", "price": 33.90, "description": "A seca e a miséria no sertão nordestino.", "image_url": "livro-19.jpg", "category": "livro", "stock": 42, "release_date": "2024-02-22"},
    {"title": "A Hora da Estrela", "author": "Clarice Lispector", "price": 31.90, "description": "A história de Macabéa e sua existência.", "image_url": "livro-20.jpg", "category": "livro", "stock": 48, "release_date": "2024-02-24"},
    {"title": "O Primo Basílio", "author": "Eça de Queirós", "price": 37.90, "description": "Romance realista português.", "image_url": "livro-21.jpg", "category": "livro", "stock": 30, "release_date": "2024-02-26"},
    {"title": "A Moreninha", "author": "Joaquim Manuel de Macedo", "price": 28.90, "description": "Romance romântico brasileiro.", "image_url": "livro-22.jpg", "category": "livro", "stock": 50, "release_date": "2024-02-28"},
    
    # Mais Fantasia
    {"title": "Eragon", "author": "Christopher Paolini", "price": 47.90, "description": "A saga do cavaleiro de dragões.", "image_url": "livro-23.jpg", "category": "fantasia", "stock": 40, "release_date": "2024-03-01"},
    {"title": "A Guerra dos Tronos", "author": "George R.R. Martin", "price": 69.90, "description": "O jogo de tronos começa.", "image_url": "livro-24.jpg", "category": "fantasia", "stock": 35, "release_date": "2024-03-03"},
    {"title": "O Nome do Vento", "author": "Patrick Rothfuss", "price": 59.90, "description": "A história de Kvothe, o Sem-Sangue.", "image_url": "livro-25.jpg", "category": "fantasia", "stock": 30, "release_date": "2024-03-05"},
    {"title": "Mistborn: O Império Final", "author": "Brandon Sanderson", "price": 54.90, "description": "Um mundo onde a cinza cai do céu.", "image_url": "livro-26.jpg", "category": "fantasia", "stock": 38, "release_date": "2024-03-07"},
    {"title": "A Roda do Tempo", "author": "Robert Jordan", "price": 64.90, "description": "A profecia do Dragão Renascido.", "image_url": "livro-27.jpg", "category": "fantasia", "stock": 32, "release_date": "2024-03-09"},
    
    # Mais Ficção Científica
    {"title": "Fundação", "author": "Isaac Asimov", "price": 52.90, "description": "O futuro da humanidade na galáxia.", "image_url": "livro-28.jpg", "category": "ficcao", "stock": 40, "release_date": "2024-03-11"},
    {"title": "Neuromancer", "author": "William Gibson", "price": 48.90, "description": "O clássico cyberpunk.", "image_url": "livro-29.jpg", "category": "ficcao", "stock": 35, "release_date": "2024-03-13"},
    {"title": "Duna", "author": "Frank Herbert", "price": 67.90, "description": "A saga épica do deserto de Arrakis.", "image_url": "livro-30.jpg", "category": "ficcao", "stock": 30, "release_date": "2024-03-15"},
    {"title": "O Guia do Mochileiro das Galáxias", "author": "Douglas Adams", "price": 42.90, "description": "Comédia sci-fi intergaláctica.", "image_url": "livro-31.jpg", "category": "ficcao", "stock": 50, "release_date": "2024-03-17"},
    {"title": "Eu, Robô", "author": "Isaac Asimov", "price": 39.90, "description": "As três leis da robótica.", "image_url": "livro-32.jpg", "category": "ficcao", "stock": 45, "release_date": "2024-03-19"},
    
    # Mais Terror
    {"title": "O Exorcista", "author": "William Peter Blatty", "price": 46.90, "description": "Possessão demoníaca e terror.", "image_url": "livro-33.jpg", "category": "terror", "stock": 35, "release_date": "2024-03-21"},
    {"title": "A Assombração da Casa da Colina", "author": "Shirley Jackson", "price": 43.90, "description": "Terror psicológico em uma mansão.", "image_url": "livro-34.jpg", "category": "terror", "stock": 30, "release_date": "2024-03-23"},
    {"title": "O Chamado de Cthulhu", "author": "H.P. Lovecraft", "price": 41.90, "description": "Horror cósmico lovecraftiano.", "image_url": "livro-35.jpg", "category": "terror", "stock": 40, "release_date": "2024-03-25"},
    {"title": "Cemitério Maldito", "author": "Stephen King", "price": 51.90, "description": "Às vezes, é melhor deixar os mortos descansarem.", "image_url": "livro-36.jpg", "category": "terror", "stock": 32, "release_date": "2024-03-27"},
    
    # Livros Adicionais
    {"title": "O Código Da Vinci", "author": "Dan Brown", "price": 49.90, "description": "Mistério e conspiração religiosa.", "image_url": "livro-37.jpg", "category": "livro", "stock": 45, "release_date": "2024-03-29"},
    {"title": "A Menina que Roubava Livros", "author": "Markus Zusak", "price": 44.90, "description": "Uma história sobre livros e guerra.", "image_url": "livro-38.jpg", "category": "livro", "stock": 50, "release_date": "2024-03-31"},
    {"title": "O Caçador de Pipas", "author": "Khaled Hosseini", "price": 42.90, "description": "Amizade e redenção no Afeganistão.", "image_url": "livro-39.jpg", "category": "livro", "stock": 40, "release_date": "2024-04-02"},
    {"title": "A Culpa é das Estrelas", "author": "John Green", "price": 37.90, "description": "Um romance sobre amor e perda.", "image_url": "livro-40.jpg", "category": "livro", "stock": 55, "release_date": "2024-04-04"},
    {"title": "O Diário de Anne Frank", "author": "Anne Frank", "price": 35.90, "description": "O relato real de uma menina durante o Holocausto.", "image_url": "livro-41.jpg", "category": "livro", "stock": 60, "release_date": "2024-04-06"},
    {"title": "A Revolução dos Bichos", "author": "George Orwell", "price": 33.90, "description": "Alegoria política sobre totalitarismo.", "image_url": "livro-42.jpg", "category": "livro", "stock": 45, "release_date": "2024-04-08"},
    {"title": "O Retrato de Dorian Gray", "author": "Oscar Wilde", "price": 39.90, "description": "Beleza, decadência e moralidade.", "image_url": "livro-43.jpg", "category": "livro", "stock": 38, "release_date": "2024-04-10"},
    {"title": "Crime e Castigo", "author": "Fiódor Dostoiévski", "price": 56.90, "description": "Psicologia e moralidade na Rússia czarista.", "image_url": "livro-44.jpg", "category": "livro", "stock": 30, "release_date": "2024-04-12"},
    {"title": "Os Miseráveis", "author": "Victor Hugo", "price": 72.90, "description": "Épico sobre justiça e redenção.", "image_url": "livro-45.jpg", "category": "livro", "stock": 25, "release_date": "2024-04-14"},
    {"title": "Cem Anos de Solidão", "author": "Gabriel García Márquez", "price": 54.90, "description": "Realismo mágico na família Buendía.", "image_url": "livro-46.jpg", "category": "livro", "stock": 35, "release_date": "2024-04-16"},
    {"title": "O Amor nos Tempos do Cólera", "author": "Gabriel García Márquez", "price": 48.90, "description": "Romance que atravessa décadas.", "image_url": "livro-47.jpg", "category": "livro", "stock": 40, "release_date": "2024-04-18"},
    {"title": "A Metamorfose", "author": "Franz Kafka", "price": 29.90, "description": "A transformação de Gregor Samsa.", "image_url": "livro-48.jpg", "category": "livro", "stock": 50, "release_date": "2024-04-20"},
]

def seed_database():
    """Popula o banco de dados com os livros"""
    with app.app_context():
        # Verificar se já existem livros
        existing_count = Book.query.count()
        if existing_count > 0:
            print(f"⚠️  Banco já contém {existing_count} livros.")
            response = input("Deseja limpar e recriar? (s/n): ")
            if response.lower() != 's':
                print("❌ Operação cancelada.")
                return
            
            # Limpar tabela
            Book.query.delete()
            db.session.commit()
            print("✅ Tabela limpa.")
        
        # Inserir livros
        print(f"\n📚 Inserindo {len(BOOKS_DATA)} livros no banco de dados...")
        
        for book_data in BOOKS_DATA:
            book = Book(**book_data)
            db.session.add(book)
        
        db.session.commit()
        
        # Verificar
        final_count = Book.query.count()
        print(f"\n✅ Seed concluído com sucesso!")
        print(f"📊 Total de livros no banco: {final_count}")
        
        # Mostrar alguns exemplos
        print("\n📖 Exemplos de livros cadastrados:")
        sample_books = Book.query.limit(5).all()
        for book in sample_books:
            print(f"   - {book.title} ({book.author}) - R$ {book.price:.2f}")

if __name__ == '__main__':
    print("=" * 60)
    print("🌱 SEED DO BANCO DE DADOS - NORDES STUDIO")
    print("=" * 60)
    seed_database()
