"""
Funções auxiliares
"""
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import current_app

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_upload_file(file, prefix=''):
    """
    Salva um arquivo de upload com nome seguro e timestamp
    
    Args:
        file: Arquivo do request.files
        prefix: Prefixo para o nome do arquivo
    
    Returns:
        str: Nome do arquivo salvo ou None se falhar
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if prefix:
        new_filename = f"{prefix}_{timestamp}_{filename}"
    else:
        new_filename = f"{timestamp}_{filename}"
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    filepath = os.path.join(upload_folder, new_filename)
    
    try:
        file.save(filepath)
        return new_filename
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
        return None

def delete_upload_file(filename):
    """
    Remove um arquivo de upload
    
    Args:
        filename: Nome do arquivo a ser removido
    
    Returns:
        bool: True se removido com sucesso, False caso contrário
    """
    if not filename:
        return False
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    filepath = os.path.join(upload_folder, filename)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Erro ao remover arquivo: {e}")
            return False
    
    return False

def format_price(price):
    """Formata preço para o padrão brasileiro"""
    return f"R$ {price:.2f}".replace('.', ',')

def parse_price(price_str):
    """Converte string de preço para float"""
    try:
        # Remove 'R$' e espaços, troca ',' por '.'
        clean_price = price_str.replace('R$', '').replace(' ', '').replace(',', '.')
        return float(clean_price)
    except:
        return 0.0
