"""Utils for flask app.

Main method is decorator for authorization
"""
from flask import request, jsonify
from flask import current_app
from functools import wraps
from flask_app.models import UserModel
import jwt
INVALID_MSG = {
    ".login_errors": "Registration and/or Login required",
}
EXPIRED_MSG = {
    ".login_errors": "Expired token. Please login again.",
}


def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get("Authorization", "").split()


        if len(auth_headers) != 2:
            return jsonify({"status": "error", "message": INVALID_MSG})
        elif auth_headers[1] == 'null':
            return jsonify({"status": "error", "message": INVALID_MSG})

        try:
            token = auth_headers[1]
            if token == 'loggedOut':
                return jsonify({"status": "error", "message": INVALID_MSG})

            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
            user = UserModel.find_by_username(username=data["sub"])
            if not user:
                raise RuntimeError("User not found")
            return f(user, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            current_app.logger.warn("User Token expired!")
            return jsonify({"status": "error", "message": EXPIRED_MSG})

        except (jwt.InvalidTokenError, Exception) as e:
            current_app.logger.error('Hitting Here: {e}'.format(e=e))
            return jsonify({"status": "error", "message": INVALID_MSG})

    return _verify


def get_user(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get("Authorization", "").split()
        try:
            token = auth_headers[1]
            if token == 'loggedOut':
                return f('', *args, **kwargs)

            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
            user = UserModel.find_by_username(username=data["sub"])
            return f(user, *args, **kwargs)
        except Exception as e:
            return f('', *args, **kwargs)
    return _verify
