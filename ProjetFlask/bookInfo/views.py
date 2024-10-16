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
from flask import render_template, flash

class AuthorForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])

class BookForm(FlaskForm):
    id = HiddenField('id')
    title = StringField('Titre', validators=[DataRequired()])
    price = StringField('Prix', validators=[DataRequired()])



from flask_login import login_required

@app.route("/edit/author/<int:id>")
@login_required
def edit_author(id):
    a = get_author(id)
    f = AuthorForm(id=a.id, name=a.name)
    return render_template(
    "edit-author.html",
    author=a, form=f)


@app.route("/edit/book/<int:id>")
@login_required
def edit_book(id):
    b = get_book(id)
    f = BookForm(id = b.id, title = b.title, price = b.price)
    return render_template(
    "edit-book.html",
    book=b, form=f)
    

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

@app.route("/save/book/<int:idBook>", methods=("POST",))
def save_book(idBook):
    f = BookForm()
    if f.validate_on_submit():
        id = int(f.id.data)
        b = get_book(id)
        b.title = f.title.data
        db.session.commit()
        return redirect(url_for('edit_book', id = b.id))
    b = get_book(int(f.id.data))
    return render_template(
        "edit-book.html",
        book=b,
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

@app.route("/save/newBook", methods=('POST',))
def save_new_book():
    f = BookForm()
    if f.validate_on_submit():
        b = Book(title=f.title.data, price=f.price.data)
        db.session.add(b)
        db.session.commit()
        return redirect(url_for('books'))
    return render_template(
    "new-book.html",
    form=f)

@app.route("/books")
def books():
    return render_template(
        "books.html",
        books=get_sample()
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

@app.route("/book/newBook")
@login_required
def newBook():
    id = Book.query.count() +1
    form = BookForm(id=id)
    if form.validate_on_submit():
        if form.title.data =="":
            flash("Le titre est obligatoire")
            return redirect(url_for('newBook'))
        elif form.price.data =="":
            flash("Le prix est obligatoire")
            return redirect(url_for('newBook'))
        elif form.url.data =="":
            flash("L'url est obligatoire")
            return redirect(url_for('newBook'))
        elif form.img.data =="":
            flash("L'image est obligatoire")
            return redirect(url_for('newBook'))
        new_book = Book(id=id, title=form.title.data, price=form.price.data, url=form.url.data, img=form.img.data)
        db.session.add(new_book)
        db.session.commit()
        flash("Livre ajouté avec succès !")
        return redirect(url_for('books'))
    return render_template(
        "new-book.html",
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

@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        new_book = Book(title=form.title.data, price=form.price.data, url=form.url.data, img=form.img.data)
        db.session.add(new_book)
        db.session.commit()
        flash('Livre enregistré avec succès !')
        return redirect(url_for('books'))  # Rediriger vers la liste des auteurs

    return render_template('add_book.html', form=form)

from wtforms import PasswordField, SubmitField
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


class RegisterForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('S\'inscrire')

@app.route("/sign-in/", methods=["GET", "POST"])
def sign_in():
    f = RegisterForm()
    if f.validate_on_submit():
        error = None
        user = User.query.get(f.username.data)
        if user is not None:
            error = "Ce nom d'utilisateur existe déjà."
            flash(error)
            return render_template("sign_in.html", form=f, error=error)
        if not is_username_secure(f.username.data):
            error = "Le nom d'utilisateur doit contenir au moins 5 caractères et ne doit pas contenir d'espace."
            flash(error)
            return render_template("sign_in.html", form=f, error=error)
        if not is_password_secure(f.password.data):
            error = "Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre."
            flash(error)
            return render_template("sign_in.html", form=f, error=error)
        user = User(f.username.data, f.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("sign_in.html", form=f, error=None)

@app.route("/delete/author/<int:id>")
def delete_author(id):
    a = get_author(id)
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('authors'))

@app.route("/delete/book/<int:id>")
def delete_book(id):
    b = get_book(id)
    db.session.delete(b)
    db.session.commit()
    return redirect(url_for('books'))

@app.route("/favorites/<string:username>")
def favorites(username):
    user = User.query.get(username)
    books = user.favorite_books.all()
    return render_template(
        "favorites.html",
        user=user,
        books=books
    )

@app.route("/add_favorite/<string:username>/<int:book_id>")
def add_favorite(username, book_id):
    user = User.query.get(username)
    book = Book.query.get(book_id)
    user.add_to_favorites(book)
    return redirect(url_for('detail', id=book_id))

@app.route("/remove_favorite/<string:username>/<int:book_id>")
def remove_favorite(username, book_id):
    user = User.query.get(username)
    book = Book.query.get(book_id)
    user.remove_from_favorites(book)
    return redirect(url_for('detail', id=book_id))


