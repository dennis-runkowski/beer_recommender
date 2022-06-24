"""Flask extensions used."""
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail

bootstrap = Bootstrap()
csrf = CSRFProtect()
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
