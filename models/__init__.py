from flask_sqlalchemy import SQLAlchemy

# Global db object (importable everywhere)
db = SQLAlchemy()

# Import models so they register with SQLAlchemy
from .user import User
from .question import Question
