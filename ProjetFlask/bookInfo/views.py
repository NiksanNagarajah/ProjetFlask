from .app import app
from flask import render_template
from .models import *

@app.route('/')
def home():
    return render_template(
        'home.html', 
        title="My Books !",
        books=get_sample())

@app.route("/detail/<id>")
def detail(id):
    books = get_sample()
    book = get_sample()[int(id)-1]
    print(book)
    return render_template(
        'detail.html',
        book=book,
    )

from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired
from flask import render_template

class AuthorForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])

from flask_login import login_required

@app.route("/edit/author/<int:id>")
@login_required
def edit_author(id):
    a = get_author(id)
    f = AuthorForm(id=a.id, name=a.name)
    return render_template(
    "edit-author.html",
    author=a, form=f)

from flask import url_for, redirect, render_template
from .app import db
from .models import Author

@app.route("/save/author/", methods=("POST",))
def save_author():
    f = AuthorForm()
    if f.validate_on_submit():
        id = int(f.id.data)
        a = get_author(id)
        a.name = f.name.data
        db.session.commit()
        return redirect(url_for('edit_author', id=a.id))
    # Si la validation échoue, on récupère à nouveau l'auteur
    a = get_author(int(f.id.data))
    return render_template(
        "edit-author.html",  # Correction du nom du template
        author=a,
        form=f
    )

@app.route("/save/newAuthor", methods=("POST",))
def save_new_author():
    f = AuthorForm()
    if f.validate_on_submit():
        a = Author(name=f.name.data)
        db.session.add(a)
        db.session.commit()
        return redirect(url_for('authors'))
    return render_template(
    "new-author.html",
    form=f)

@app.route("/authors")
def authors():
    return render_template(
        "authors.html",
        authors=get_authors()
        )

@app.route("/author/newAuthor")
@login_required
def newAuthor():
    id = Author.query.count() + 1
    form = AuthorForm(id=id)
    if form.validate_on_submit():
        if form.name.data == "":
            flash('Le nom de l\'auteur est obligatoire !')
            return redirect(url_for('newAuthor'))
        new_author = Author(name=form.name.data)
        db.session.add(new_author)
        db.session.commit()
        flash('Auteur enregistré avec succès !')
        return redirect(url_for('authors'))
    return render_template(
        "new-author.html",
        form=form
        )


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    form = AuthorForm()
    if form.validate_on_submit():
        new_author = Author(name=form.name.data)
        db.session.add(new_author)
        db.session.commit()
        flash('Auteur enregistré avec succès !')
        return redirect(url_for('authors'))  # Rediriger vers la liste des auteurs

    return render_template('add_author.html', form=form)

from wtforms import PasswordField
from .models import User
from hashlib import sha256

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    next = HiddenField()

    def get_authenticated_user(self):
        user = User.query.get(self.username.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None


from flask import request, redirect, render_template, url_for
from flask_login import login_user

@app.route("/login/", methods=["GET", "POST"])
def login():
    f = LoginForm()
    
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            next_page = f.next.data or url_for("home")
            return redirect(next_page)
    
    return render_template("login.html", form=f)



from flask_login import logout_user
from flask import redirect, url_for

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))

