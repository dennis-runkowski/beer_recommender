"""Main Flask app for the website and api."""
from redisearch import Client
from flask import Flask
from flask_app.extensions import bootstrap, csrf, db, mail, bcrypt
import flask_app.views as views
from flask import g
from cold_ones_pkg import get_config
import logging

CONFIG = get_config()


def setup_config():
    """
    Helper function to configure environment based on config.
    """
    if CONFIG.get("environment", "server") == 'production':
        return 'config.ProductionConfig'
    else:
        return 'config.TestingConfig'


def create_app():
    """Main application factory."""
    app = Flask(__name__)

    # Use helper function to source environment from config
    environment = setup_config()
    app.config.from_object(environment)

    # Setup logging level
    if environment == 'config.ProductionConfig':
        logging.basicConfig(level=logging.WARN)
    else:
        logging.basicConfig(level=logging.DEBUG)

    @app.before_request
    def before_request():
        g.db = redis_client("beer_index")

    @app.before_first_request
    def create_tables():
        db.create_all()

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app):
    """Register flask extensions."""
    bootstrap.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)


def register_blueprints(app):
    """Register flask blueprints."""
    app.register_blueprint(views.home_blueprint)
    app.register_blueprint(views.api_blueprint, url_prefix='/api/v1/')
    app.register_blueprint(views.user_blueprint, url_prefix='/users/v1/')


def redis_client(index_name, port=6379, password=False):
    """Get redis client

    Args:
        index_name (str): Redis index name
        port (int): Port for redis
        password (str): Redis password
    Returns:
        obj: redis client
    """
    client = Client(
        index_name=index_name,
        host='localhost',
        port=port,
        password=password
    )
    return client


def register_errors(app):
    """Register flask error handling."""
    # TODO
    pass
