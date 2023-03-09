from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from sqlalchemy.sql import func

login = LoginManager()
db = SQLAlchemy()
 
class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'
 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    privilege_level = db.Column(db.String(16), default="User", nullable=False) #Could be User, Admin, or SuperAdmin also could be an integer but used string for this example

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
 
class PostModel(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.Column(db.String(100), db.ForeignKey('users.username'), nullable=False)
    status = db.Column(db.String, default="Draft")



@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))