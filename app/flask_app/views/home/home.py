"""Main collection of views."""
import os
from flask import Blueprint, render_template, url_for, current_app as app


# Blue print for the main display
home_blueprint = Blueprint(
    'home',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@home_blueprint.route('/', methods=['GET'])
def home():
    """Main home page."""

    return render_template(
        'main.html',
    )


# Cache Buster for static files
@home_blueprint.context_processor
def override_url_for():
    """Cache Buster for static files"""
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    """Timestamp method for cache busting"""
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
