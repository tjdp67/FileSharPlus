from functools import wraps

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, make_response
from .models import users
from . import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

auth = Blueprint('auth', __name__)


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.cookies.get('user_id')
        if user_id:
            # Retrieve the user based on the ID
            query = text(f"SELECT * FROM users WHERE id = '{user_id}'")
            user = db.session.execute(query).first()
            if user:
                # Pass the user ID to the wrapped function
                return func(user, *args, **kwargs)
        # User is not authenticated or user ID is not found, redirect to the login page
        else:
            return func(None, *args, **kwargs)
    return wrapper


@auth.route('/example')
def example_route():
    current_app.logger.debug('This is a debug message')
    current_app.logger.info('This is an info message')
    current_app.logger.warning('This is a warning message')
    current_app.logger.error('This is an error message')
    return 'Example Route'


@auth.route('/login', methods=['GET', 'POST'])
@authenticate
def login(user):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = text(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
        user = db.session.execute(query).first()

        if user:
            # Cookie
            response = make_response(redirect("/"))
            response.set_cookie('user_id', f'{user.id}')
            current_app.logger.info(f'LOGIN: id:{user.id} name:{username} password: {password}')
            return response
        else:
            flash("Login failed", category="error")
    return render_template("login.html", user=user)


@auth.route('/logout')
def logout():
    user_id = request.cookies.get('user_id')
    response = make_response(redirect('/login'))
    response.delete_cookie('user_id')
    current_app.logger.info(f'LOGOUT: user_id:{user_id}')
    flash("Logged out!", category="success")
    return response


@auth.route('/signup', methods=['GET', 'POST'])
@authenticate
def signup(user):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if 'permissions' in request.form:
            permissions = request.form['permissions']
        else:
            permissions = 'user'

        query = text(f"INSERT INTO users (username, password, permissions) VALUES ('{username}', '{password}', '{permissions}')")
        db.session.execute(query)
        db.session.commit()

        query = text(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
        user = db.session.execute(query).first()
        current_app.logger.info(f'SIGNUP: id:{user.id} name:{username} password: {password}')

        query = text(f"INSERT INTO directories (name, user_id) VALUES ('files','{user.id}')")
        db.session.execute(query)
        db.session.commit()
        current_app.logger.info(f'DIRECTORY_CREATED: user_id:{user.id} name:files')

        if user:
            # Cookie
            response = make_response(redirect("/"))
            response.set_cookie('user_id', f'{user.id}')
            current_app.logger.info(f'LOGIN: id:{user.id} name:{username} password: {password}')
            return response

    return render_template("sign_up.html", user=user)
