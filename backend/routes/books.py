"""
Rotas de Livros
"""
from flask import Blueprint, request, jsonify
from utils.decorators import token_required, admin_required
from services.book_service import BookService

books_bp = Blueprint('books', __name__, url_prefix='/api/books')

@books_bp.route('', methods=['GET'])
def get_books():
    """Lista todos os livros"""
    # Parâmetros de filtro opcionais
    category = request.args.get('category')
    search = request.args.get('search')
    
    if category:
        books = BookService.get_books_by_category(category)
    elif search:
        books = BookService.search_books(search)
    else:
        books = BookService.get_all_books()
    
    return jsonify([book.to_dict() for book in books])

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Busca um livro específico"""
    book = BookService.get_book_by_id(book_id)
    
    if not book:
        return jsonify({'message': 'Livro não encontrado'}), 404
    
    return jsonify(book.to_dict())

@books_bp.route('', methods=['POST'])
@token_required
@admin_required
def create_book(current_user):
    """Cria um novo livro (apenas admin)"""
    data = request.form
    file = request.files.get('image')
    
    # Validar campos obrigatórios
    required_fields = ['title', 'author', 'price']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'Campo {field} é obrigatório'}), 400
    
    # Criar livro
    book, error = BookService.create_book(
        title=data.get('title'),
        author=data.get('author'),
        price=data.get('price'),
        description=data.get('description'),
        category=data.get('category'),
        stock=data.get('stock', 0),
        release_date=data.get('release_date'),
        image_file=file
    )
    
    if error:
        return jsonify({'message': error}), 400
    
    return jsonify({
        'message': 'Livro criado com sucesso',
        'book': book.to_dict()
    }), 201

@books_bp.route('/<int:book_id>', methods=['PUT'])
@token_required
@admin_required
def update_book(current_user, book_id):
    """Atualiza um livro existente (apenas admin)"""
    data = request.form
    file = request.files.get('image')
    
    # Atualizar livro
    book, error = BookService.update_book(
        book_id=book_id,
        title=data.get('title'),
        author=data.get('author'),
        price=data.get('price'),
        description=data.get('description'),
        category=data.get('category'),
        stock=data.get('stock'),
        release_date=data.get('release_date'),
        image_file=file
    )
    
    if error:
        status_code = 404 if 'não encontrado' in error else 400
        return jsonify({'message': error}), status_code
    
    return jsonify({
        'message': 'Livro atualizado com sucesso',
        'book': book.to_dict()
    })

@books_bp.route('/<int:book_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_book(current_user, book_id):
    """Remove um livro (apenas admin)"""
    success, error = BookService.delete_book(book_id)
    
    if not success:
        status_code = 404 if 'não encontrado' in error else 400
        return jsonify({'message': error}), status_code
    
    return jsonify({'message': 'Livro excluído com sucesso'})
