from datetime import datetime
from flask import Blueprint, render_template, request, flash, jsonify, redirect, send_from_directory, session, send_file, current_app
from . import db
from .auth import authenticate
import os
from sqlalchemy import text

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@authenticate
def home(user):
    return render_template("home.html", user=user)


@views.route('/dashboard', methods=['GET', 'POST'])
@authenticate
def dashboard(user):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = text(f"UPDATE users SET username = '{username}', password = '{password}' WHERE id = '{user.id}'")
        db.session.execute(query)
        db.session.commit()
        current_app.logger.info(f'UPDATE_USER: id:{user.id} name:{username} password: {password}')
        return render_template("dashboard.html", user=user)
    return render_template("dashboard.html", user=user)


@views.route('/admin', methods=['GET', 'POST', 'DELETE'])
@authenticate
def admin(user):
    if request.method == 'GET':
        query = text(f"SELECT * FROM users")
        users = db.session.execute(query).fetchall()

    if request.method == 'DELETE':
        id = request.json['user_id']
        query = text(f"DELETE FROM users WHERE id='{id}'")
        db.session.execute(query)
        query = text(f"DELETE FROM blog_posts WHERE user_id = '{id}'")
        db.session.execute(query)
        query = text(f"DELETE FROM comments WHERE user_id = '{id}'")
        db.session.execute(query)
        query = text(f"DELETE FROM files WHERE user_id = '{id}'")
        db.session.execute(query)
        query = text(f"DELETE FROM directories WHERE user_id = '{id}'")
        db.session.execute(query)
        query = text(f"DELETE FROM tickets WHERE user_id = '{id}'")
        db.session.execute(query)
        query = text(f"DELETE FROM ticket_messages WHERE user_id = '{id}'")
        db.session.execute(query)
        db.session.commit()

        current_app.logger.info(f'USER_DELETED: admin_id:{user.id} user_id:{id}')
        flash('User Deleted!', category='success')
        return jsonify({'message': 'User deleted successfully'})
    return render_template('admin.html', user=user, users=users)


@views.route('/search')
@authenticate
def search(user):
    query = text(f"SELECT * FROM users")
    users = db.session.execute(query).fetchall()
    return render_template('search_users.html', user=user, users=users)


@views.route('/profile/<user_id>')
@authenticate
def user_profile(user, user_id):
    # Fetch the user data based on the user_id
    query = text(f"SELECT * FROM users WHERE id = '{user_id}'")
    tmp_profile = db.session.execute(query).first()
    if tmp_profile:
        # Fetch the files associated with the user
        query = text(f"SELECT * FROM files WHERE user_id = '{tmp_profile.id}'")
        files = db.session.execute(query).fetchall()
        # Render the user profile template with the user and file data

        new_files = []
        query = text(f"SELECT * FROM files WHERE user_id='{tmp_profile.id}'")
        user_files = db.session.execute(query).fetchall()
        for file in user_files:
            query = text(f"SELECT * FROM directories WHERE id = '{file.directory_id}'")
            tmp_directory = db.session.execute(query).first()
            directory_name = tmp_directory.name
            new_file = {
                'id': file.id,
                'file_name': file.file_name,
                'date': file.date,
                'user_id': file.user_id,
                'privacy': file.privacy,
                'directory_id': file.directory_id,
                'directory_name': directory_name
            }
            new_files.append(new_file)

        query = text(f"SELECT * FROM directories WHERE user_id = '{tmp_profile.id}'")
        directories = db.session.execute(query).fetchall()
        return render_template('user_profile.html', user=user, username=tmp_profile.username, files=new_files, directories=directories)
    else:
        # Handle case when user is not found
        flash("User not found!", category="error")
        return redirect("/search")


# Chat:
messages = []
@views.route('/chat')
def chat():
    return render_template('chat.html')


@views.route('/send_message', methods=['POST'])
def send_message():
    sender = request.form['sender']
    receiver = request.form['receiver']
    message = request.form['message']

    # Store the message in the messages list
    messages.append({
        'sender': sender,
        'receiver': receiver,
        'message': message
    })

    return jsonify({'success': True})


@views.route('/get_messages', methods=['GET'])
def get_messages():
    receiver = request.args.get('receiver')

    # Filter messages for the specified receiver
    received_messages = [msg for msg in messages if msg['receiver'] == receiver]

    return jsonify({'messages': received_messages})
# Serve Files
@views.route('/uploads/<path:filename>')
def serve_upload(filename):
    basedir = os.path.abspath(os.path.dirname(__file__))
    uploads_folder = f"uploads"
    upload_path = os.path.join(basedir, f'{uploads_folder}')
    return send_from_directory(f'{upload_path}', filename)


# Render Time User-Friendly
def render_time():
    current_time = datetime.utcnow()
    formatted_time = current_time.strftime("%B %d, %Y %H:%M:%S")
    return formatted_time

