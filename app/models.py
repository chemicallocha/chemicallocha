from app import app
from datetime import *
from app import db
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
from flask_sqlalchemy import SQLAlchemy
import sys


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    fullname = db.Column(db.String(50))
    occupation = db.Column(db.String(50))
    hobby = db.Column(db.String(50))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # this function can also take different sizes
    def avatar(self, size=128):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


    


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    company = db.Column(db.String(100))
    message = db.Column(db.String(500))

    def __repr__(self):
        return '< Name : {}, Message : {}>'.format(self.name, self.message)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class PostCategory(db.Model):
    __tablename__ = 'postcategory'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String, nullable=False)
    posts = db.relationship('Post', backref='postcategory')

    def __repr__(self):
        return '<Post Category %s>' %(self.category_name)

    def len_category(self,categoryID):
        cat = PostCategory().query.get(int(categoryID))
        return len(cat.posts)

post_tags  = db.Table('post_tags',  
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50))
    heading = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    body = db.Column(db.String)
    post_url = db.Column(db.String(140))
    comments = db.relationship('Comment', backref='comment_on_page', lazy='dynamic')
    category_id = db.Column(db.Integer, db.ForeignKey('postcategory.id'))
    likes = db.Column(db.Integer, default=1)
    tags = db.relationship('Tag', secondary=post_tags,
        backref=db.backref('post_tags', lazy='dynamic')
            )
    thumbnail = db.Column(db.String)
    def get_post_url(self):
        return self.post_url
    def get_post_id(self):
        return self.id   
    def latest_posts(self):
        return Post.query.order_by(Post.timestamp.desc())
    def post_author(self, user):
        return Post.query.filter_by(author=user).first()
    def post_author_avatar(self, user, size):
        author = User.query.filter_by(username=user).first()
        return author.avatar(size)
    def post_thumbnail(self, postID):
        return Post().query.get(postID).thumbnail

    def category(self, postID):
        post = Post().query.get(int(postID))
        category = post.postcategory.category_name
        return category
    def categoryID(self, name):
        return PostCategory().query.filter_by(category_name=name).first().id
    def related(self, postID):
        post= Post().query.get(int(postID))
        postcategory = post.postcategory
        return postcategory.posts[:5]
    def remove_tags(self, postID):
        tags = post_tags.query.filter_by(post_id=postID).all()
        db.session.delete(tags)
        db.session.commit()




class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String)

    posts = db.relationship('Post', secondary=post_tags,
        backref=db.backref('post_tags', lazy='dynamic')
            )
            
    def new_tag(self, tag):
        if len(tag) >=1:
            new_tag = Tag(tag_name=tag)
            db.session.add(new_tag)
            db.session.commit()
            return 'tag added'
                    
    def __repr__(self):
        return '<Tag: {}>'.format(self.tag_name)

class NewsLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<subscriber {}>'.format(self.email)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(400))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved = db.Column(db.Integer, default='0')

    def __repr__(self):
        return '<Comment %r >' %(self.comment)

    def username(self, id):
        return User.query.get(int(id)).username

    def get_post_heading(self, postID):
        post = Post.query.get(int(postID))
        return post.heading

    def get_user_avatar(self, userID, size):
        user = User.query.get(int(userID))
        return User.avatar(user, size)

    def comments_on_user_posts(self, userID):
        user = User.query.get(int(userID))
        user_posts = Post().query.filter_by(author=user.username).all()
        pending_comments = []
        for post in user_posts:
            for comment in Comment().query.filter_by(post_id=post.id).all():
                if comment.approved == 0:
                    pending_comments.append(comment)

        return pending_comments
   

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String)
    filedata = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def username(self, id):
        return User.query.get(int(id)).username
    def filetype(self, filename):
        filetype = filename.split('.')[1].upper()
        return str(filetype)
