from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    fullname = StringField('Full Name', validators=[Length(min=1,max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    fullname = StringField('Full Name', validators=[Length(max=50)])
    occupation = StringField('Occupation', validators=[Length(max=50)])
    hobby = StringField('Your Hobbies', validators=[Length(max=50)])
    about_me = TextAreaField('About Myself', validators=[Length(min=0, max=150)])
    submit = SubmitField('Submit')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    company = StringField('Company / Website')
    message = TextAreaField('Message')
    submit = SubmitField('Submit')

class ArticleForm(FlaskForm):
    heading = StringField('Title', validators=[DataRequired(), Length(min=1, max=250)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=30)])
    submit = SubmitField('Submit')

class NewsLetterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=1)])
    submit = SubmitField('Subscribe')

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('Comment')

class FileUploadForm(FlaskForm):
    submit = SubmitField('Upload')

class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])

    