from datetime import datetime
from flask import Blueprint, render_template, request, flash, jsonify, redirect, send_from_directory, session, send_file, current_app
from . import db
from .auth import authenticate
from .views import render_time
import os
from sqlalchemy import text

file_serve = Blueprint('file_serve', __name__)


# Everything File related
@file_serve.route("/upload", methods=['GET', 'POST', 'DELETE'])
@authenticate
def upload(user):
    basedir = os.path.abspath(os.path.dirname(__file__))
    if request.method == 'POST':
        # Get directory name Default is: files
        directory_id = request.form['directory']
        query = text(f"SELECT * FROM directories WHERE id = '{directory_id}'")
        directory = db.session.execute(query).first()
        user_folder = f"uploads/{user.username}/{directory.name}"
        upload_path = os.path.join(basedir, f'{user_folder}')

        # Create user-specific directory if it doesn't exist
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        file = request.files['file']
        privacy_option = request.form.get('privacy')
        if file.filename != '':
            # Query
            query = text(
                f"INSERT INTO files (file_name, user_id, directory_id, privacy, date) VALUES ('{file.filename}', '{user.id}','{directory.id}','{privacy_option}','{render_time()}')")
            db.session.execute(query)
            db.session.commit()

            # File Upload to user Folder
            file_path = os.path.join(upload_path, file.filename)
            file.save(file_path)

            flash('File Upload successful!', category='success')
            current_app.logger.info(f'FILE_UPLOAD: user_id:{user.id} file:{file.filename} directory_id: {directory.id} directory_name: {directory.name}')
        else:
            flash('No File detected!', category='error')
    elif request.method == 'DELETE':
        id = request.json['file_id']

        # Get Filename and create path
        query = text(f"SELECT * FROM files WHERE id='{id}'")
        file = db.session.execute(query).first()

        # Get Directory Name
        query = text(f"SELECT * FROM directories WHERE id = '{file.directory_id}'")
        directory = db.session.execute(query).first()
        # Get user Folder Path
        user_folder = f"uploads/{user.username}/{directory.name}"
        upload_path = os.path.join(basedir, f'{user_folder}')

        file_path = os.path.join(upload_path, file.file_name)

        # Delete in database
        query = text(f"DELETE FROM files WHERE id='{id}'")
        db.session.execute(query)
        query = text(f"DELETE FROM blog_posts WHERE file_id = '{id}'")
        db.session.execute(query)
        db.session.commit()
        current_app.logger.info(
            f'FILE_DELETE: user_id:{user.id} file:{file.file_name} directory_id: {directory.id} directory_name: {directory.name}')
        flash('File Deleted!', category='success')

        # Delete File in Folder
        if os.path.exists(file_path):
            # Delete the file from the server
            os.remove(file_path)
            return jsonify({'message': 'Image deleted successfully'})
        else:
            return jsonify({'message': 'Image file not found'})
    if user:
        # Adapt files to have directory name:
        new_files = []
        query = text(f"SELECT * FROM files WHERE user_id='{user.id}'")
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

        query = text(f"SELECT * FROM directories WHERE user_id = '{user.id}'")
        directories = db.session.execute(query).fetchall()
    return render_template("upload.html", user=user, files=new_files, directories=directories)


@file_serve.route('/toggle-privacy/<int:file_id>')
def toggle_privacy(file_id):
    # Find the file with the given file_id
    query = text(f"SELECT * FROM files WHERE id='{file_id}'")
    file = db.session.execute(query).first()
    if file:
        # Toggle the privacy
        if file.privacy == "public":
            query = text(f"UPDATE files SET privacy = 'private' WHERE id = '{file.id}'")
            db.session.execute(query)
            db.session.commit()
            current_app.logger.info(f'FILE_UPDATE_PRIVACY: id:{file.id} file:{file.file_name} privacy:{file.privacy } directory_id: {file.directory_id}')
            query = text(f"DELETE FROM blog_posts WHERE file_id = '{file.id}'")
            current_app.logger.info(f'BLOG_DELETE: with file_id:{file.id}')
            db.session.execute(query)
            db.session.commit()
        else:
            query = text(f"UPDATE files SET privacy = 'public' WHERE id = '{file.id}'")
            current_app.logger.info(f'FILE_UPDATE_PRIVACY: id:{file.id} file:{file.file_name} privacy:{file.privacy } directory_id: {file.directory_id}')
            db.session.execute(query)
            db.session.commit()
        return redirect('/upload')
    else:
        return 'File not found'


@file_serve.route('/download/<int:file_id>')
@authenticate
def download_file(user, file_id):
    # Find the file with the given file_id
    query = text(f"SELECT * FROM files WHERE id='{file_id}'")
    file = db.session.execute(query).first()
    # BaseDir
    basedir = os.path.abspath(os.path.dirname(__file__))
    uploads_folder = f"uploads"
    upload_path = os.path.join(basedir, f'{uploads_folder}')

    # Get Username of File Owner
    query = text(f"SELECT * FROM users WHERE id='{file.user_id}'")
    user = db.session.execute(query).first()

    # Get Directory Name
    query = text(f"SELECT * FROM directories WHERE id = '{file.directory_id}'")
    directory = db.session.execute(query).first()

    if file:
        file_path = os.path.join(upload_path, f'{user.username}')
        file_path = os.path.join(file_path, f'{directory.name}')
        file_path = os.path.join(file_path, f'{file.file_name}')
        current_app.logger.info(f"FILE_DOWNLOAD: user_id:{user.id} file_id:{file.id} file_name:{file.file_name}")
        return send_file(file_path, as_attachment=True)
    else:
        return 'File not found'


@file_serve.route('/create-directory', methods=['POST'])
@authenticate
def create_directory(user):
    directory_name = request.form.get('directoryName')

    # Create Path:
    basedir = os.path.abspath(os.path.dirname(__file__))
    user_folder = f"uploads/{user.username}/{directory_name}"
    directory_path = os.path.join(basedir, f'{user_folder}')
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    else:
        flash("Directory already exists!", category='error')
        return redirect("/upload")

    query = text(f"INSERT INTO directories (name, user_id) VALUES ('{directory_name}','{user.id}')")
    db.session.execute(query)
    db.session.commit()

    # Return a response indicating the directory was created successfully
    current_app.logger.info(f'DIRECTORY_CREATED: user_id:{user.id} name:{directory_name}')
    flash("Directory Created!", category="success")
    return redirect('/upload')
