from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import desc
from models import UserModel, db, login, PostModel
from forms import LoginForm, RegisterForm, BlogForm
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
    return render_template(
        "index.html", current_username=get_current_username(), page_title="Home"
    )


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
    return render_template(
        "login.html",
        form=form,
        current_username=get_current_username(),
        page_title="Login",
    )


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
    return render_template(
        "register.html", message=message, form=form, page_title="Register"
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.is_json:
        user_input = str(request.args.get("user_input")).lower().replace(" ", "-")
        if PostModel.query.filter_by(slug=user_input).first():
            response = jsonify("True")
            response.status_code = 200
            return response

    form = BlogForm()
    if form.validate_on_submit():  # Change me
        post = PostModel(
            title=form.title.data,
            slug=form.slug.data.lower().replace(" ", "-"),
            content=form.content.data,
            author=current_user.username,
        )
        db.session.add(post)
        db.session.commit()
        return redirect("/")
    return render_template(
        "create.html",
        form=form,
        current_username=get_current_username(),
        page_title="Create Post",
    )


@app.route("/my-posts")
def my_posts():
    posts = (
        PostModel.query.filter_by(author=get_current_username())
        .order_by(desc(PostModel.created_at))
        .all()
    )
    return render_template(
        "my-posts.html",
        posts=posts,
        current_username=get_current_username(),
        page_title="My Posts",
    )


@app.route("/edit/<slug>", methods=["GET", "POST"])
@login_required
def edit(slug):
    post = PostModel.query.filter_by(slug=slug).first()
    if (
        post.author != get_current_username()
        and current_user.privilege_level != "Admin"
    ):
        return redirect("/")

    form = BlogForm()
    if form.validate_on_submit():  # Change me
        edit = PostModel.query.filter_by(slug=slug).first()
        edit.title = form.title.data
        edit.slug = slug = form.slug.data.lower().replace(" ", "-")
        edit.content = form.content.data
        edit.status = "Draft"
        db.session.add(edit)
        db.session.commit()
        return redirect("/my-posts")
    form.content.data = post.content
    return render_template(
        "edit.html",
        post=post,
        form=form,
        current_username=get_current_username(),
        page_title=f"Edit {post.title}",
    )


@app.route("/delete/<id>")
@login_required
def delete(id):
    post = PostModel.query.filter_by(id=id).first()
    if post.author == get_current_username() or current_user.privilege_level == "Admin":
        db.session.delete(post)
        db.session.commit()
        return redirect("/my-posts")
    else:
        return redirect("/")


@app.route("/posts")
def browse():
    posts = (
        PostModel.query.filter_by(status="Published")
        .order_by(desc(PostModel.created_at))
        .all()
    )
    return render_template(
        "browse_posts.html",
        posts=posts,
        current_username=get_current_username(),
        page_title="Browse Posts",
    )


@app.route("/posts/<slug>")
def view_post(slug):
    post = PostModel.query.filter_by(slug=slug).first()
    if post.status == "Published":
        return render_template(
            "post.html",
            post=post,
            current_username=get_current_username(),
            page_title=post.title,
        )
    return redirect("/")


@app.route("/posts/<slug>/change-status")
def change_status(slug):
    post = PostModel.query.filter_by(slug=slug).first()
    if post.author == get_current_username():
        if post.status == "Draft":
            post.status = "Review"
        else:
            post.status = "Draft"
        db.session.add(post)
        db.session.commit()
        return redirect("/my-posts")
    else:
        return redirect("/")


@app.route("/posts/<slug>/publish")
def publish_post(slug):
    if current_user.privilege_level == "Admin":
        post = PostModel.query.filter_by(slug=slug).first()
        post.status = "Published"
        db.session.add(post)
        db.session.commit()
        return redirect("/admin/review-posts")
    else:
        return redirect("/")


@app.route("/admin/review-posts")
@login_required
def review_posts():
    if current_user.privilege_level == "Admin":
        posts = (
            PostModel.query.filter_by(status="Review")
            .order_by(desc(PostModel.created_at))
            .all()
        )
        return render_template(
            "review-posts.html",
            posts=posts,
            current_username=get_current_username(),
            page_title="Review Posts",
        )
    else:
        return redirect("/")


@app.route("/admin/users")
@login_required
def manage_accounts():
    if current_user.privilege_level == "Admin":
        users = UserModel.query.all()
        return render_template(
            "manage-accounts.html",
            users=users,
            current_username=get_current_username(),
            page_title="Users",
        )
    else:
        return redirect("/")


@app.route("/admin/users/<id>/reset-password")
@login_required
def reset_password(id):
    if current_user.privilege_level == "Admin":
        user = UserModel.query.filter_by(id=id).first()
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        return redirect("/admin/users")
    else:
        return redirect("/")


@app.route("/admin/users/<id>/delete")
@login_required
def delete_account(id):
    if current_user.privilege_level == "Admin":
        user = UserModel.query.filter_by(id=id).first()
        db.session.delete(user)
        posts = PostModel.query.filter_by(author=user.username).all()
        for post in posts:
            db.session.delete(post)
        db.session.commit()
        return redirect("/admin/users")
    else:
        return redirect("/")


@app.route("/admin/users/<id>/change-privilege")
@login_required
def change_privilege(id):
    if current_user.privilege_level == "Admin":
        user = UserModel.query.filter_by(id=id).first()
        if user.privilege_level == "Admin":
            user.privilege_level = "User"
        else:
            user.privilege_level = "Admin"
        db.session.add(user)
        db.session.commit()
        return redirect("/admin/users")
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
