from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from datetime import timedelta
db = SQLAlchemy()
jwt = JWTManager()
DEFAULT_JWT_EXPIRES = timedelta(days=36500) 