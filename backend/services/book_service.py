"""
Serviço de Livros
Contém toda a lógica de negócio relacionada a livros
"""
from extensions import db
from models.book import Book
from utils.helpers import save_upload_file, delete_upload_file

class BookService:
    """Serviço de gerenciamento de livros"""
    
    @staticmethod
    def get_all_books():
        """
        Retorna todos os livros
        
        Returns:
            list: Lista de livros
        """
        return Book.query.all()
    
    @staticmethod
    def get_book_by_id(book_id):
        """
        Busca um livro por ID
        
        Args:
            book_id: ID do livro
        
        Returns:
            Book: Objeto do livro ou None
        """
        return Book.query.get(book_id)
    
    @staticmethod
    def get_books_by_category(category):
        """
        Busca livros por categoria
        
        Args:
            category: Categoria dos livros
        
        Returns:
            list: Lista de livros
        """
        return Book.query.filter_by(category=category).all()
    
    @staticmethod
    def search_books(query):
        """
        Busca livros por título ou autor
        
        Args:
            query: Termo de busca
        
        Returns:
            list: Lista de livros encontrados
        """
        search_term = f"%{query}%"
        return Book.query.filter(
            (Book.title.ilike(search_term)) | (Book.author.ilike(search_term))
        ).all()
    
    @staticmethod
    def create_book(title, author, price, description=None, category=None, 
                   stock=0, release_date=None, image_file=None):
        """
        Cria um novo livro
        
        Args:
            title: Título do livro
            author: Autor do livro
            price: Preço do livro
            description: Descrição (opcional)
            category: Categoria (opcional)
            stock: Quantidade em estoque
            release_date: Data de lançamento (opcional)
            image_file: Arquivo de imagem (opcional)
        
        Returns:
            tuple: (book, error_message)
        """
        # Salvar imagem se fornecida
        image_filename = None
        if image_file:
            image_filename = save_upload_file(image_file)
            if not image_filename:
                return None, 'Erro ao salvar imagem'
        
        # Criar livro
        book = Book(
            title=title,
            author=author,
            price=float(price),
            description=description,
            category=category,
            stock=int(stock),
            release_date=release_date,
            image_url=image_filename
        )
        
        try:
            db.session.add(book)
            db.session.commit()
            return book, None
        except Exception as e:
            db.session.rollback()
            # Remover imagem se falhou
            if image_filename:
                delete_upload_file(image_filename)
            return None, f'Erro ao criar livro: {str(e)}'
    
    @staticmethod
    def update_book(book_id, title=None, author=None, price=None, description=None,
                   category=None, stock=None, release_date=None, image_file=None):
        """
        Atualiza um livro existente
        
        Args:
            book_id: ID do livro
            title: Novo título (opcional)
            author: Novo autor (opcional)
            price: Novo preço (opcional)
            description: Nova descrição (opcional)
            category: Nova categoria (opcional)
            stock: Novo estoque (opcional)
            release_date: Nova data de lançamento (opcional)
            image_file: Novo arquivo de imagem (opcional)
        
        Returns:
            tuple: (book, error_message)
        """
        book = Book.query.get(book_id)
        
        if not book:
            return None, 'Livro não encontrado'
        
        # Atualizar campos se fornecidos
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if price is not None:
            book.price = float(price)
        if description is not None:
            book.description = description
        if category is not None:
            book.category = category
        if stock is not None:
            book.stock = int(stock)
        if release_date is not None:
            book.release_date = release_date
        
        # Atualizar imagem se fornecida
        if image_file:
            new_image = save_upload_file(image_file)
            if new_image:
                # Remover imagem antiga
                if book.image_url:
                    delete_upload_file(book.image_url)
                book.image_url = new_image
            else:
                return None, 'Erro ao salvar nova imagem'
        
        try:
            db.session.commit()
            return book, None
        except Exception as e:
            db.session.rollback()
            return None, f'Erro ao atualizar livro: {str(e)}'
    
    @staticmethod
    def delete_book(book_id):
        """
        Remove um livro
        
        Args:
            book_id: ID do livro
        
        Returns:
            tuple: (success, error_message)
        """
        book = Book.query.get(book_id)
        
        if not book:
            return False, 'Livro não encontrado'
        
        # Remover imagem se existir
        if book.image_url:
            delete_upload_file(book.image_url)
        
        try:
            db.session.delete(book)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f'Erro ao remover livro: {str(e)}'
