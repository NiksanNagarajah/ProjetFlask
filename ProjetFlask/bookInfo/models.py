from .app import db

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    
    def __repr__(self):
        return "<Author (%d) %s>" % (self.id, self.name)

# Table d'association pour les favoris
book_avis = db.Table('book_avis',
    db.Column('id', db.Integer, primary_key=True), 
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), nullable=False),
    db.Column('user_id', db.String(80), db.ForeignKey('user.username'), nullable=False),
    db.Column('avis', db.String(255), nullable=False)
)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    title = db.Column(db.String(100))
    url = db.Column(db.String(100))
    img = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
    author = db.relationship("Author", backref=db.backref("books", lazy="dynamic"))

    avis_livre = db.relationship('User', secondary=book_avis, lazy='dynamic', backref=db.backref('avis_de', lazy='dynamic'))


    def add_avis(self, user, avis_text):
        """Ajoute un avis pour un livre donné par un utilisateur sans mise à jour."""
        new_avis = book_avis.insert().values(book_id=self.id, user_id=user.username, avis=avis_text)
        db.session.execute(new_avis)
        db.session.commit()


    def get_avis(self):
        return db.session.query(book_avis).filter_by(book_id=self.id).all()


    def __repr__(self):
        return "<Book (%d) %s>" % (self.id, self.title) + self.author.name + self.url + self.img

def get_sample():
    # return Book.query.all()
    return Book.query.limit(10).all()

def get_all_books():
    return Book.query.all()

def get_author(id):
    return Author.query.get(id)

def get_authors():
    return Author.query.all()

def get_book(id):
    return Book.query.get(id)


from flask_login import UserMixin

# Table d'association pour les favoris
user_favorites = db.Table('user_favorites',
    db.Column('user_id', db.String(80), db.ForeignKey('user.username'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80))
    role = db.Column(db.String(20), default='user')

    favorite_books = db.relationship('Book', secondary=user_favorites, lazy='dynamic', backref=db.backref('favorited_by', lazy='dynamic'))

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)
    
    def set_password(self, password):
        from hashlib import sha256
        m = sha256()
        m.update(password.encode())
        self.password = m.hexdigest()

    def get_id(self):
        return self.username
    
    def is_admin(self):
        return self.role == 'admin'
    
    def add_to_favorites(self, book):
        if not self.is_favorite(book):
            self.favorite_books.append(book)
            db.session.commit()

    def remove_from_favorites(self, book):
        if self.is_favorite(book):
            self.favorite_books.remove(book)
            db.session.commit()

    def is_favorite(self, book):
        return self.favorite_books.filter_by(id=book.id).count() > 0


from .app import login_manager

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

def is_username_secure(username):
    return len(username) >= 5 and ' ' not in username

def is_password_secure(password):
    return (len(password) >= 8 and
            any(char.isdigit() for char in password) and
            any(char.islower() for char in password) and
            any(char.isupper() for char in password))


