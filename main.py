from flask import Flask, render_template, request, redirect, flash, session
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel, db, login, PostModel
from forms import LoginForm, RegisterForm, BlogForm
from urllib.request import urlopen
from datetime import date
from flask_ckeditor import CKEditor


app = Flask(__name__)
app.secret_key = "super secret key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/images"

db.init_app(app)
login.init_app(app)
login.login_view = "login"
ckeditor = CKEditor(app)


def get_current_username():
    if current_user.is_authenticated:
        return current_user.username
    else:
        return "Guest"


@app.route("/") 
def index():
    return render_template("index.html", current_username=get_current_username())

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(username=form.username.data).first()
        if user:
            if user.check_password(form.password.data):
                login_user(user)
                return redirect("/")
        return "<h1>Invalid username or password</h1>"
    return render_template("login.html", form=form, current_username=get_current_username())

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect("/")
    message = ""
    form = RegisterForm()
    if form.validate_on_submit():
        query = UserModel.query.filter_by(username=form.username.data).first()
        # Validation checks
        # if form.username.data == query.username:
        #     message = "Username already exists"
        # elif form.password.data != form.confirm_password.data:
        #    message = "Passwords do not match"
        # # Else add the user to the database
        # else:
        user = UserModel(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html", message=message, form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = BlogForm()
    if form.validate_on_submit(): #Change me
        post = PostModel(title=form.title.data, slug=form.slug.data, content=form.content.data, author=current_user.username)
        db.session.add(post)
        db.session.commit()
        return redirect("/")
    return render_template("create.html", form=form, current_username=get_current_username())

@app.route("/my-posts")
def my_posts():
    posts = PostModel.query.filter_by(author=get_current_username()).all()
    return render_template("my-posts.html", posts=posts, current_username=get_current_username())

@app.route("/edit/<slug>", methods=["GET", "POST"])
@login_required
def edit(slug):
    post = PostModel.query.filter_by(slug=slug).first()
    if post.author != get_current_username():
        return redirect("/")
    
    form = BlogForm()
    if form.validate_on_submit(): #Change me
        edit = PostModel.query.filter_by(slug=slug).first()
        edit.title = form.title.data
        edit.slug = form.slug.data
        edit.content = form.content.data
        db.session.add(edit)
        db.session.commit()
        return redirect("/my-posts")
    form.content.data = post.content
    return render_template("edit.html", post=post, form=form, current_username=get_current_username())

@app.route("/delete/<id>")
@login_required
def delete(id):
    post = PostModel.query.filter_by(id=id).first()
    if post.author != get_current_username():
        return redirect("/")
    db.session.delete(post)
    db.session.commit()
    return redirect("/")

@app.route("/posts")
def browse():
    posts = PostModel.query.all()
    return render_template("browse_posts.html", posts=posts, current_username=get_current_username())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
