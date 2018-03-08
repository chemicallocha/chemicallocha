import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rajatomar788'
    if os.environ.get('DATABASE_URL') is None:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    elif os.environ.get('EXTRA_DATABASE') is not None:
        SQLALCHEMY_DATABASE_URI = os.environ['EXTRA_DATABASE']
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
      
    MAX_SEARCH_RESULTS = 50

    POSTS_PER_PAGE = 20

    basedir = basedir

    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    MAX_CONTENT_PATH = 16*1024*1024

    #mail server settings
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USERNAME = 'Raja'
    MAIL_PASSWORD = 'raja788'

    #administrator list
    ADMINS = ['rajatomar788@gmail.com']
