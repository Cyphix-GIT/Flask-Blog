from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, IntegerRangeField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, NumberRange
from flask_ckeditor import CKEditorField

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=16)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=35)])

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=16)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=35)])
    confirm_password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=35), EqualTo('password', message='Passwords must match')])#Issue where form isn't valid but no message is displayed

class BlogForm(FlaskForm):
    title = StringField('title', validators=[InputRequired(), Length(min=4, max=32)])
    slug    = StringField('slug', validators=[InputRequired(), Length(min=1, max=64)])
    content = CKEditorField('content', validators=[InputRequired(), Length(min=8)])
    #category = SelectField('category', choices=[('General', 'General'), ('Tech', 'Tech'), ('Food', 'Food'), ('Other', 'Other')], validators=[InputRequired()])
    submit = SubmitField('Save to drafts')