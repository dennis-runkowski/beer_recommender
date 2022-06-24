"""Blueprint for user management, signup and login"""
from flask import Blueprint, jsonify, request, render_template
from flask import current_app as app
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
import jwt
from flask_app.extensions import bcrypt, mail
from flask_app.models import UserModel
from flask_app.utils import token_required

# Blue print for the main page
user_blueprint = Blueprint(
    'users',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@user_blueprint.route('/signup', methods=['POST'])
def sign_up():
    """
    Endpoint to validate and signup users
    """
    data = request.form
    username = data.get('username_signup', None)
    email = data.get('email_signup', None)
    password = data.get('password_signup', None)
    confirm_password = data.get('password_confirm_signup', None)
    errors = {}
    status = 0
    # Validate form
    email_query = UserModel.find_by_email(email)
    if email_query:
        status = 1
        errors["#signup_email_error"] = "This email already exists!"
    if not email:
        status = 1
        errors["#signup_email_error"] = "Please enter a email address!"

    if not username:
        status = 1
        errors["#signup_username_error"] = "Please enter a username!"
    else:
        check_username = UserModel.find_by_username(username)
        if check_username:
            status = 1
            errors["#signup_username_error"] = "This username already exists!"

    if not password:
        status = 1
        errors["#signup_confirm_error"] = "Please enter a password!"

    elif len(password) < 8:
        status = 1
        errors["#signup_password_error"] = (
            "Password must be longer than 8 characters!")

    elif password != confirm_password:
        status = 1
        errors["#signup_confirm_error"] = "Passwords do not match!"

    if status == 1:
        app.logger.warn(errors)
        return jsonify({"status": "error", "message": errors})

    try:
        password = bcrypt.generate_password_hash(password)
        user = UserModel(
            username,
            password,
            email
        )
        user.save_to_db()
    except Exception as e:
        app.logger.error(e)
        errors["#signup_error"] = (
            "There was an unknown error when creating your account!"
        )
        return jsonify({"status": "error", "message": errors})

    return jsonify({"status": "success", "message": ""})


@user_blueprint.route('/login', methods=['POST'])
def login():
    """
    Create login token for user. Tokens are set to expire in 2 hours
    Requires form with the following fields.
        username and password

    Returns:
        dict with encoded jwt token with username, current time, and expiration
    """
    data = request.form
    user = UserModel.authenticate(**data)

    if not user:
        error = {
            "#login_errors": "Invalid credentials"
        }
        return jsonify({"status": "error", "message": error})

    token = jwt.encode(
        {
            'sub': user.username,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=2440)
        },
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )
    return jsonify({"status": "success", "message": token})


@user_blueprint.route('/login_check', methods=['GET'])
@token_required
def check_login(current_user):
    """
    Check if a user is logged into the app and token is not expired

    Args:
        current_user (str): username

    Returns:
         dict with success/fail. message contains username on success.
    """
    if current_user.username:
        user_name = current_user.username
    else:
        user_name = ""
    return jsonify({"status": "success", "message": user_name})


@user_blueprint.route('/forgot_password', methods=['POST'])
def forgot_password():
    """Validate email and reset password email."""

    data = request.form
    # Ensure email exists in db
    email_query = UserModel.find_by_email(data.get("forgot_email"))

    if not email_query:
        error = {
            "#forgot_errors": "No User with this email exists!"
        }
        return jsonify({"status": "error", "message": error})
    else:
        password_reset_serializer = URLSafeTimedSerializer(
            app.config['SECRET_KEY']
        )

        token = password_reset_serializer.dumps(
            email_query.email,
            salt='password-reset-salt'
        )
        res = send_email(
                email_query.email,
                token,
                'password_reset_email.html',
                'password_reset_email.txt',
                'Cold Ones - Reset password'
            )
        if res == "Fail":
            error = {
                "#forgot_errors": "Failed to send reset!"
            }
            return jsonify({"status": "error", "message": error})

        return jsonify({"status": "success"})


@user_blueprint.route('/reset_password', methods=['POST'])
def reset_password():
    """reset password"""
    data = request.form
    token = data.get("reset_token")
    password = data.get("reset_password")
    error = {
        "#reset_errors": "Invalid reset token!"
    }
    try:
        password_reset_serializer = URLSafeTimedSerializer(
            app.config['SECRET_KEY']
        )
        email = password_reset_serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=3600
        )
    except Exception as e:
        app.logger.error("Invalid reset token - %s", e)

        return jsonify({"status": "error", "message": error})

    if not email:
        return jsonify({"status": "error", "message": error})

    # Validate new password
    if len(password) < 8:
        return jsonify({
            "status": "error",
            "message": {
                "#reset_errors": "Password must be longer then 8 characters"
            }
        })
    email_query = UserModel.find_by_email(email)
    email_query.password = bcrypt.generate_password_hash(
        password
    )
    email_query.save_to_db()
    return jsonify({"status": "success", "message": "Reset Password!"})


def send_email(email, token, template, text, subject):
    """Send email to reset password

    Args:
        email (str): email to the user
        token (str): token to reset password
        template (str): path to the template file
        text (str): path to the text template file
        subject (str): subject of the email

    Returns:
        str success or fail

    """
    try:
        msg = Message(
            subject=subject,
            sender=app.config.get("MAIL_USERNAME"),
            recipients=[email],
        )
        body_html = render_template(
            template,
            token=token
        )
        body_text = render_template(
            text,
            token=token
        )
        msg.body = body_text
        msg.html = body_html
        mail.send(msg)

        return "Success"
    except Exception as e:
        app.logger.error("Email failed to send for password reset - %s", e)
        return "Fail"
