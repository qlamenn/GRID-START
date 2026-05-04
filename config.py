import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'grid-start-secret-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///f1.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    API_F1_KEY = '944ba80b98c4929e4f18be6fc662c6e1'