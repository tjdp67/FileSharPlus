from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    #DO NOT REMOVE, THIS IS INTENDED
    app.jinja_env.autoescape = False
    #------------------------------
    # Logging
    app.logger.setLevel(logging.DEBUG)
    # Configure logging to separate files
    basedir = os.path.abspath(os.path.dirname(__file__))
    log_dir = "log"
    log_path = os.path.join(basedir, f'{log_dir}')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_debug = f'{log_path}/debug.log'
    log_info = f'{log_path}/info.log'
    log_warning = f'{log_path}/warning.log'
    log_error = f'{log_path}/error.log'

    # Create handlers for each log level
    handler_debug = logging.FileHandler(log_debug)
    handler_info = logging.FileHandler(log_info)
    handler_warning = logging.FileHandler(log_warning)
    handler_error = logging.FileHandler(log_error)

    # Set log levels for the handlers
    handler_debug.setLevel(logging.DEBUG)
    handler_info.setLevel(logging.INFO)
    handler_warning.setLevel(logging.WARNING)
    handler_error.setLevel(logging.ERROR)

    # Add the handlers to the Flask logger
    app.logger.addHandler(handler_debug)
    app.logger.addHandler(handler_info)
    app.logger.addHandler(handler_warning)
    app.logger.addHandler(handler_error)

    # SECRET KEY for session
    app.config['SECRET_KEY'] = '5up3rdup3r53cr3tk3y'

    # DATABASE path
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, f'{DB_NAME}')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    # Init Database
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .blogs import blogs
    from .support import support
    from .file_serve import file_serve

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(blogs, url_prefix='/')
    app.register_blueprint(support, url_prefix='/')
    app.register_blueprint(file_serve, url_prefix='/')

    from .models import users, comments, blog_posts, files, tickets, ticket_messages, directories

    with app.app_context():
        db.create_all()
        # Create default users
        default_users = [
            {'username': 'admin', 'password': 'admin123', 'permissions': 'admin'},
            {'username': 'john_doe', 'password': 'password123', 'permissions': 'user'},
            {'username': 'jane_smith', 'password': 'qwerty', 'permissions': 'user'},
            {'username': 'alex_brown', 'password': 'welcome', 'permissions': 'user'}
        ]

        default_directories = [
            {'name': 'files', 'user_id': 1},
            {'name': 'files', 'user_id': 2},
            {'name': 'files', 'user_id': 3},
            {'name': 'files', 'user_id': 4}
        ]

        default_blog_posts = [
            {'message': 'Welcome to our blog!', 'user_id': 1, 'file_id': 'None'},
            {'message': 'Check out our latest updates!', 'user_id': 2, 'file_id': 'None'},
            {'message': 'Sharing insights and knowledge', 'user_id': 3, 'file_id': 'None'},
            {'message': 'Exploring new ideas', 'user_id': 4, 'file_id': 'None'}
        ]

        default_comments = [
            {'content': 'Great post!', 'user_id': 2, 'blog_id': 1},
            {'content': 'Interesting read!', 'user_id': 3, 'blog_id': 1},
            {'content': 'I have a question. Can you elaborate?', 'user_id': 4, 'blog_id': 1},
            {'content': 'Looking forward to more updates!', 'user_id': 2, 'blog_id': 2},
            {'content': 'Thanks for sharing!', 'user_id': 3, 'blog_id': 2},
            {'content': 'Keep up the good work!', 'user_id': 4, 'blog_id': 2},
        ]

        # Create default users and directories
        for user_data in default_users:
            username = user_data['username']
            password = user_data['password']
            permissions = user_data['permissions']

            user = users.query.filter_by(username=username).first()
            if not user:
                user = users(username=username, password=password, permissions=permissions)
                db.session.add(user)

        for directory_data in default_directories:
            name = directory_data['name']
            user_id = directory_data['user_id']

            directory = directories.query.filter_by(name=name, user_id=user_id).first()
            if not directory:
                directory = directories(name=name, user_id=user_id)
                db.session.add(directory)

        # Create default blog posts
        for post_data in default_blog_posts:
            message = post_data['message']
            user_id = post_data['user_id']
            file_id = post_data['file_id']

            post = blog_posts.query.filter_by(message=message, user_id=user_id).first()
            if not post:
                post = blog_posts(message=message, user_id=user_id, date=datetime.now(), file_id=file_id)
                db.session.add(post)

        # Create default comments
        for comment_data in default_comments:
            content = comment_data['content']
            user_id = comment_data['user_id']
            blog_id = comment_data['blog_id']

            comment = comments.query.filter_by(content=content, user_id=user_id, blog_id=blog_id).first()
            if not comment:
                comment = comments(content=content, user_id=user_id, blog_id=blog_id, date=datetime.now())
                db.session.add(comment)

        db.session.commit()

    return app