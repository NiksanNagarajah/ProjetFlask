from .app import app
from flask import render_template, jsonify
from .models import *
from flask import request, redirect, url_for, render_template
from flask_login import current_user, login_required
from wtforms import PasswordField, SubmitField
from sqlalchemy import func
from flask_wtf.file import FileField, FileAllowed 
from werkzeug.utils import secure_filename
import os

@app.route('/')
def home():
    return render_template(
        'home.html', 
        books=get_sample())

@app.route("/detail/<id>")
def detail(id):
    book = get_book(id)
    avis = book.get_avis()
    
    return render_template(
        'detail.html',
        book=book,
        avis=avis  
    )


from flask import request, redirect, url_for, render_template
from flask_login import current_user

@app.route("/add_avis/<int:book_id>", methods=["POST"])
@login_required
def add_avis(book_id):
    book = get_book(book_id)
    avis_text = request.form.get("avis")
    
    if avis_text:
        book.add_avis(current_user, avis_text)
        flash("Votre avis a été ajouté ou mis à jour avec succès.")
    else:
        flash("L'avis ne peut pas être vide.")
    
    return redirect(url_for('detail', id=book_id))

from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired
from flask import render_template, flash

class AuthorForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])
    submit = SubmitField('Enregistrer')

class BookForm(FlaskForm):
    id = HiddenField('id')
    title = StringField('Titre', validators=[DataRequired()])
    price = StringField('Prix', validators=[DataRequired()])
    author = StringField('Auteur', validators=[DataRequired()])
    img = FileField('Image')
    submit = SubmitField('Enregistrer')

    def prix_valide(self, price):
        try:
            float(price)
            return True
        except:
            return False
    
    def auteur_valide(self, author):
        le_auteur = Author.query.filter_by(name=author).first()
        if le_auteur is None:
            return False
        return True

from flask_login import login_required

@app.route("/edit/author/<int:id>")
@login_required
def edit_author(id):
    a = get_author(id)
    f = AuthorForm(id=a.id, name=a.name)
    return render_template(
    "edit-author.html",
    author=a, form=f)


@app.route("/edit/book/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_book(id):
    error = None
    b = get_book(id)
    f = BookForm(id=b.id, title=b.title, price=b.price, author=b.author.name)
    if f.validate_on_submit():
        if not f.prix_valide(f.price.data):
            flash("Le prix doit être un nombre valide.")
            return render_template('edit-book.html', book=b, form=f, error="Le prix doit être un nombre valide.")
        b.title = f.title.data
        b.price = float(f.price.data) 
        db.session.commit()

        flash("Livre mis à jour avec succès.")
        return redirect(url_for('edit_book', id=b.id))
    return render_template("edit-book.html", book=b, form=f, error=error)

    

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
    a = get_author(int(f.id.data))
    return render_template(
        "edit-author.html", 
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
    sort = request.args.get("sort", "id") 
    if sort == "id":
        les_auteurs_avec_nb_livres = db.session.query(Author, db.func.count(Book.id)).outerjoin(Book).group_by(Author.id).order_by(Author.id).all()
    elif sort == "name":
        les_auteurs_avec_nb_livres = db.session.query(Author, db.func.count(Book.id)).outerjoin(Book).group_by(Author.id).order_by(Author.name).all()
    elif sort == "nbLivre":
        les_auteurs_avec_nb_livres = db.session.query(Author, db.func.count(Book.id)).outerjoin(Book).group_by(Author.id).order_by(db.func.count(Book.id)).all()
    else:
        les_auteurs_avec_nb_livres = db.session.query(Author, db.func.count(Book.id)).outerjoin(Book).group_by(Author.id).order_by(Author.id).all()

    return render_template(
        "authors.html",
        authors=les_auteurs_avec_nb_livres,
        sort=sort
    )

@app.route("/indisponible")
def indisponible():
    return render_template("indisponible.html")

@app.route("/books")
def books():
    sort = request.args.get("sort", "id")
    if sort == "id":
        books = Book.query.order_by(Book.id).all()
    elif sort == "titre":
        books = Book.query.order_by(Book.title).all()
    elif sort == "prix":
        books = Book.query.order_by(Book.price).all()
    else:
        books = Book.query.order_by(Book.id).all()
    return render_template(
        "books.html",
        books=books
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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@app.route("/book/newBook", methods=['GET', 'POST'])
@login_required
def newBook():
    id = db.session.query(func.max(Book.id)).scalar() + 1
    f = BookForm()
    if f.validate_on_submit():
        if f.prix_valide(f.price.data) == False:
            flash("Le prix doit être un nombre.")
            return render_template('new-book.html', form=f, error="Le prix doit être un nombre.")
        if f.auteur_valide(f.author.data) == False:
            flash("L'auteur n'existe pas.")
            return render_template('new-book.html', form=f, error="L'auteur n'existe pas.")
        if f.img.data:
            filename = secure_filename(f.img.data.filename)
            if '.' in filename and not filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                flash("Le fichier n'est pas une image.")
                return render_template('new-book.html', form=f, error="Le fichier n'est pas une image. (formats autorisés: png, jpg, jpeg)")
        else:
            filename = 'default_book.jpg'
        if f.img.data:
            filename = secure_filename(f.img.data.filename)
            img_path = os.path.join(os.getcwd(), 'bookInfo/static/images', filename)
            f.img.data.save(img_path)                    
        id_auteur = Author.query.filter_by(name=f.author.data).first()
        new_book = Book(id=id, title=f.title.data, price=f.price.data, url=url_for('indisponible') , img=filename, author_id=id_auteur.id)
        db.session.add(new_book)
        db.session.commit()
        flash("Livre ajouté avec succès !")
        return redirect(url_for('detail', id=id))
    return render_template(
        "new-book.html",
        form=f, error=None
    )



@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    form = AuthorForm()
    if form.validate_on_submit():
        new_author = Author(name=form.name.data)
        db.session.add(new_author)
        db.session.commit()
        flash('Auteur enregistré avec succès !')
        return redirect(url_for('authors')) 

    return render_template('add_author.html', form=form)

from wtforms import PasswordField, SubmitField
from .models import User
from hashlib import sha256

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    next = HiddenField()
    submit = SubmitField('Se connecter')

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
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.")
            return render_template("login.html", form=f, error="Nom d'utilisateur ou mot de passe incorrect.")
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

@app.route("/suggestions", methods=["GET"])
def suggestions():
    query = request.args.get('query', '').lower()
    books = Book.query.filter(Book.title.ilike(f"%{query}%")).all()
    les_livres = []
    for book in books:
            les_livres.append({
                'id': book.id,
                'title': book.title,
                'price': book.price,
                'img': url_for('static', filename='images/'+book.img),  
                'url_detail': url_for('detail', id=book.id)
            }) 
    authors = Author.query.filter(Author.name.ilike(f"%{query}%")).all()
    les_auteurs = []
    for author in authors:
        les_auteurs.append({
            'id': author.id,
            'name': author.name,
            'url_author': url_for('search_author', query=author.name)
        })
    return jsonify({'books': les_livres, 'authors': les_auteurs})


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get('query', '')
    filter_type = request.args.get('filter', 'all')  
    if not query:
        results = []
    else:
        if filter_type == 'books':
            results = Book.query.filter(Book.title.ilike(f"%{query}%")).all()
        elif filter_type == 'authors':
            results = Author.query.filter(Author.name.ilike(f"%{query}%")).all()
        else:
            books = Book.query.filter(Book.title.ilike(f"%{query}%")).all()
            authors = Author.query.filter(Author.name.ilike(f"%{query}%")).all()
            results = books + authors  
    return render_template(
        'search_results.html',
        query=query,
        results=results,
        filter_type=filter_type
    )

@app.route("/search_author", methods=["GET"]) 
def search_author():
    query = request.args.get('query', '')
    authors = Author.query.filter(Author.name.ilike(f"%{query}%")).all() 
    return render_template(
        'search_results.html', 
        query=query, 
        results=authors, 
        filter_type='authors'
    )

@app.route("/users")
def users():
    sort = request.args.get("sort", "username")
    if sort == "username":
        users = User.query.filter(User.username != "admin").order_by(User.username).all()
    elif sort == "role":
        users = User.query.filter(User.username != "admin").order_by(User.role).all()
    else:
        users = User.query.filter(User.username != "admin").all()
    return render_template(
        "users.html",
        users=users
    )

@app.route("/delete/user/<string:username>")
def delete_user(username):
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users'))

@app.route("/change-admin/<string:username>")
def change_role(username):
    user = User.query.get(username)
    user.role = "admin" if user.role == "user" else "user"
    db.session.commit()
    return redirect(url_for('users'))