"""Blueprint for the api."""
import hashlib
from flask import Blueprint, jsonify, render_template, url_for, request
from urllib.parse import unquote
from redisearch import Query, AutoCompleter, Suggestion
from redisearch.aggregation import AggregateRequest
from redisearch.reducers import tolist
from flask import current_app as app
from flask import g
from flask_app.models import user
from flask_app.utils import token_required, get_user

# Blue print for the api
api_blueprint = Blueprint(
    "api",
    __name__,
    template_folder="templates",
    static_folder="static"
)


@api_blueprint.route('/search', methods=['POST'])
@get_user
def search(current_user):
    """Main search endpoint.
    """
    data = request.json
    search_input = data.get("search_query")
    sort_by = data.get("sort_by", "")
    search_query = Query(search_input).with_scores().paging(0, 250).highlight()
    if sort_by == "abc":
        search_query = search_query.sort_by('title', asc=True)
    elif sort_by == "abv":
        search_query = search_query.sort_by('abv', asc=False)
    elif sort_by == "ibu":
        search_query = search_query.sort_by('ibu', asc=False)
    elif sort_by == "my_beers":
        if not current_user:
            return jsonify({
                "status": "error",
                "message": {
                    ".login_errors": "Registration and/or Login required"
                }
            })
        user_id = '{' + str(current_user.id) + '}'
        search_query = Query(
            f'@user_thumbs_up:{user_id}').with_scores().paging(
                0, 250).highlight()

    res = g.db.search(search_query)
    search_results = []

    if current_user:
        current_user = str(current_user.id)
    for i in res.docs:
        user_thumbs_down = ''
        user_thumbs_up = ''
        if current_user in i.user_thumbs_down.split(','):
            user_thumbs_down = current_user

        if current_user in i.user_thumbs_up.split(','):
            user_thumbs_up = current_user

        search_results.append({
            'id': i.id,
            'title': i.title,
            'brewer': i.brewer,
            'style': i.style,
            'description': i.description,
            'abv': i.abv,
            'ibu': i.ibu,
            'brewer_url': i.brewer_url,
            'brewer_facebook': i.brewer_facebook,
            'brewer_twitter': i.brewer_twitter,
            'brewer_instagram': i.brewer_instagram,
            'brewer_description': i.brewer_description,
            'user_thumbs_down': user_thumbs_down,
            'user_thumbs_up': user_thumbs_up
        })

    return jsonify(
        {'status': 'success', 'data': search_results, 'total': res.total}
    )


@api_blueprint.route('/autocomplete/<prefix>', methods=['GET'])
def autocomplete(prefix):
    """Autocomplete endpoint.
    """
    status = "success"
    try:
        title = AutoCompleter("beer_title_ac")
        style = AutoCompleter("beer_title_style")
        brewer = AutoCompleter("beer_title_brewer")
        fuzzy = False
        if len(prefix) > 2:
            fuzzy = True

        title_res = title.get_suggestions(prefix, fuzzy=fuzzy, num=5)
        title_res = [i.string for i in title_res]

        brewer_res = brewer.get_suggestions(prefix, fuzzy=fuzzy, num=5)
        brewer_res = [i.string for i in brewer_res]

        style_res = style.get_suggestions(prefix, fuzzy=fuzzy, num=5)
        style_res = [i.string for i in style_res]

        res = {
            "titles": title_res,
            "styles": style_res,
            "brewer": brewer_res
        }
    except Exception as e:
        print(e)
        res = {}
        status = "error"
    return jsonify({"status": status, "data": res})


@api_blueprint.route('/get_styles', methods=['GET'])
def get_style():
    """Get Styles endpoint.
    """
    status = "success"
    try:
        agg = AggregateRequest()

        styles = g.db.aggregate(agg.group_by('@style', tolist('@style')))
        styles = [row[1] for row in styles.rows]
        styles.sort()
        res = {
            "styles": styles,
        }
    except Exception as e:
        print(e)
        res = {}
        status = "error"
    return jsonify({"status": status, "data": res})


@api_blueprint.route('/beer_action', methods=['POST'])
@token_required
def beer_action(current_user):
    """Thumbs up/down endpoint.

    Args:
        current_user (str): username
    """
    data = request.json
    action = data.get("action")
    user_id = str(current_user.id)
    beer_id = data.get("beer_id")
    message = ''
    if action == 'down':
        message = thumbs_helper('user_thumbs_down', beer_id, user_id)
    elif action == 'up':
        message = thumbs_helper('user_thumbs_up', beer_id, user_id)
    return jsonify({"status": "success", "message": message})


@api_blueprint.route('/add_beer', methods=['POST'])
@token_required
def add_beer(current_user):
    """Add a new beer.

    Args:
        current_user (str): username
    """
    data = request.form
    error = False
    error_messages = {}
    title = data.get("beer_add", "")
    style = data.get("style_add", "")
    abv = data.get("abv_add", "")
    ibu = data.get("ibu_add", "")
    description = data.get("description_add", "")
    brewer = data.get("brewer_add", "")

    if not title:
        error = True
        error_messages["#beer_add_error"] = "Please add a title!"
    if not style:
        error = True
        error_messages["#style_add_error"] = "Please add a style!"
    if not abv:
        error = True
        error_messages["#abv_add_error"] = "Please add a abv!"
    if not ibu:
        error = True
        error_messages["#ibu_add_error"] = "Please add a ibu!"
    if not description:
        error = True
        error_messages["#description_add_error"] = "Please add a description!"
    if not brewer:
        error = True
        error_messages["#brewer_add_error"] = "Please add a brewer!"

    # Duplicate check
    if _duplicate_beer(title, brewer):
        error = True
        error_messages["#add_error"] = "This beer already exists"

    if error:
        return jsonify({"status": "error", "message": error_messages})

    # Add new beer to the typeahead
    auto = AutoCompleter("beer_title_ac")
    auto_brewer = AutoCompleter("beer_title_brewer")
    auto_style = AutoCompleter("beer_title_style")
    auto.add_suggestions(Suggestion(title))
    auto_brewer.add_suggestions(Suggestion(brewer))
    auto_style.add_suggestions(Suggestion(style))
    beer_id = f"beer:{helper_create_id(title, brewer)}"
    print(beer_id)
    g.db.redis.hset(
        beer_id,
        mapping={
            "title": title,
            "style": style,
            "user_thumbs_down": "",
            "user_thumbs_up": "",
            "description": description,
            "abv": helper_empty_value(abv, integer=True),
            "ibu": helper_empty_value(ibu, integer=True),
            "brewer": brewer,
            "brewer_description": data.get("brewer_description_add", ""),
            "brewer_url": data.get("brewer_url_add", ""),
            "brewer_facebook": data.get("brewer_facebook_add", ""),
            "brewer_instagram": data.get("brewer_twitter_add", ""),
            "brewer_twitter": data.get("brewer_instagram_add", ""),
            "user_add": str(current_user.id)
        }
    )
    return jsonify({"status": "success", "message": ''})


def _duplicate_beer(title, brewer):
    """Check if this beer already exists in the database

    Args:
        title (str): Beer name
        brewer (str): Brewer name
    Returns:
        bool: True/False
    """


def helper_create_id(title, brewer):
    """Create a hash from the beer title and brewer

    Args:
        title (str): Beer name
        brewer (str): Brewer name
    Returns:
        str: id
    """
    m = hashlib.md5()
    m.update(title.encode("utf-8"))
    m.update(brewer.encode("utf-8"))
    return m.hexdigest()[0:12]


def helper_empty_value(data, integer=False):
    """Set None to empty string
    """
    if integer:
        if not data:
            return 0.0
        return float(data)
    if not data:
        return ""
    return data


def thumbs_helper(action, beer_id, user_id):
    """Helper function for thumbs actions

    Args:
        action (str): thumbs up or down action
        beer_id (str): beer id
        user_id (str): user id
    Returns:
        str: message added or removed
    """
    message = ''
    _ids = g.db.redis.execute_command(
        'HGET', beer_id, action
    )
    _ids = _ids.split(',')
    if user_id in _ids:
        _ids.remove(user_id)
        message = 'removed'
        g.db.redis.execute_command(
            'HINCRBY',
            beer_id,
            action + '_cnt',
            -1
        )
    else:
        _ids.append(user_id)
        message = 'added'
        g.db.redis.execute_command(
            'HINCRBY',
            beer_id,
            action + '_cnt',
            1
        )

    _ids = ','.join(_ids)
    g.db.redis.execute_command(
        'HSET',
        beer_id,
        action,
        _ids
    )
    return message
