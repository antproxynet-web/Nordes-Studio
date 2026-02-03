"""
Extensões do Flask (instâncias compartilhadas)
"""
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

# Instâncias das extensões
db = SQLAlchemy()
cors = CORS()
oauth = OAuth()
