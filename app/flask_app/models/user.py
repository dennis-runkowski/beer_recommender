"""Model to create and store users to sql db."""
from flask_app.extensions import db
from flask_app.extensions import bcrypt
from datetime import datetime


class UserModel(db.Model):
    """User Model to save/create users during sign up."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.created_at = datetime.now()

    def save_to_db(self):
        """Method to save user to the db."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        """Class method to query by email."""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_username(cls, username):
        """Class method to query by email."""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        """Class method to query by id."""
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def authenticate(cls, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        if not username or not password:
            return None

        user = cls.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            return None

        return user
