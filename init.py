from app import app
SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']
from app import db
import os.path
db.create_all()