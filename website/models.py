from datetime import datetime
from . import db


class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))  # should be unique=True
    password = db.Column(db.String(150))
    permissions = db.Column(db.String(160))
    comments = db.relationship('comments', backref='users')
    files = db.relationship('files', backref='users')
    blog_posts = db.relationship('blog_posts', backref='users')
    tickets = db.relationship('tickets', backref='users')
    ticket_messages = db.relationship('ticket_messages', backref='users')


class comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    blog_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))


class blog_posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('comments', backref='blog_posts')


class files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(1500))
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    privacy = db.Column(db.String(160), server_default="private")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    directory_id = db.Column(db.Integer, db.ForeignKey('directories.id'))
    blog_posts = db.relationship('blog_posts', backref='files')

class directories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1500))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    files = db.relationship('files', backref='directories')

class tickets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1500))
    content = db.Column(db.String(10000))
    status = db.Column(db.String(15), server_default="Unsolved")
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    messages = db.relationship('ticket_messages', backref='tickets')

class ticket_messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    content = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)



