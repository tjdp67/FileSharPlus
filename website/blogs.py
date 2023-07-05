from datetime import datetime
from flask import Blueprint, render_template, request, flash, jsonify, redirect, send_from_directory, session, send_file, current_app
from . import db
from .auth import authenticate
from .views import render_time
import os
from sqlalchemy import text

blogs = Blueprint('blog', __name__)


@blogs.route('/blog', methods=['GET', 'POST', 'DELETE'])
@authenticate
def blog(user):
    if user:
        query = text(f"SELECT * FROM files WHERE user_id = '{user.id}' AND privacy = 'public'")
        private_files = db.session.execute(query).fetchall()
        query = text(f"SELECT * FROM directories WHERE user_id = '{user.id}'")
        directories = db.session.execute(query).fetchall()
    else:
        user = None
        private_files = None
        directories = None
    # POST a new BlogPost
    if request.method == 'POST':
        msg = request.form['msg']
        file = request.files['file']
        uploaded_file = request.form['uploaded_file']
        directory_id = request.form['directory']
        query = text(f"SELECT * FROM directories WHERE id = '{directory_id}'")
        directory = db.session.execute(query).first()
        if file is not None and file.filename != '':
            # File was selected, process the file
            filename = file.filename
            query = text(
                f"INSERT INTO files (file_name, user_id, directory_id, privacy, date) VALUES ('{file.filename}', '{user.id}','{directory.id}','public','{render_time()}')")
            file_id = db.session.execute(query).lastrowid
            db.session.commit()

            basedir = os.path.abspath(os.path.dirname(__file__))
            user_folder = f"uploads/{user.username}/{directory.name}"
            upload_path = os.path.join(basedir, f'{user_folder}')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file_path = os.path.join(upload_path, file.filename)
            file.save(file_path)
        elif uploaded_file != 'None':
            file_id = uploaded_file
        else:
            file_id = None
            # Handle the file accordingly
        query = text(f"INSERT INTO blog_posts (message, user_id, date, file_id) VALUES ('{msg}', '{user.id}', '{render_time()}','{file_id}')")
        db.session.execute(query)
        db.session.commit()

        current_app.logger.info(f'POST_CREATED: user_id:{user.id} post_msg:{msg}')
        flash('Blog Posted!', category='success')
    # Delete Post
    if request.method == 'DELETE':
        id = request.json['post_id']
        query = text(f"DELETE FROM blog_posts WHERE id='{id}'")
        db.session.execute(query)
        db.session.commit()

        current_app.logger.info(f'POST_DELETED: user_id:{user.id} post_id:{id}')
        flash('Blog Deleted!', category='success')
        return jsonify({'message': 'Post deleted successfully'})
    # Collect all Posts
    new_posts = []
    query = text(f'SELECT * FROM blog_posts')
    posts = db.session.execute(query).fetchall()
    for post in posts:
        query = text(f"SELECT username FROM users WHERE id='{post.user_id}'")
        tmp_user = db.session.execute(query).first()
        username = tmp_user.username
        new_post = {
            'id': post.id,
            'message': post.message,
            'date': post.date,
            'user_id': post.user_id,
            'file_id': post.file_id,
            'username': username
        }
        new_posts.append(new_post)
    return render_template("blog.html", posts=new_posts, user=user, uploaded_files=private_files, directories=directories)


@blogs.route('/blog/<int:post_id>')
@authenticate
def blog_post(user, post_id):
    # Retrieve the blog post from the database based on the post_id
    query = text(f"SELECT * FROM blog_posts WHERE id ='{post_id}'")
    post = db.session.execute(query).first()
    query = text(f"SELECT username FROM users WHERE id='{post.user_id}'")
    tmp_user = db.session.execute(query).first()
    username = tmp_user.username
    new_post = {
        'id': post.id,
        'message': post.message,
        'date': post.date,
        'user_id': post.user_id,
        'file_id': post.file_id,
        'username': username
    }

    new_comments = []
    query = text(f"SELECT * FROM comments WHERE blog_id = '{post.id}'")
    comments = db.session.execute(query)
    for comment in comments:
        query = text(f"SELECT username FROM users WHERE id='{comment.user_id}'")
        tmp_user = db.session.execute(query).first()
        username = tmp_user.username
        new_comment = {
            'id': comment.id,
            'content': comment.content,
            'date': comment.date,
            'user_id': comment.user_id,
            'blog_id': comment.blog_id,
            'username': username
        }
        new_comments.append(new_comment)
    # Render the blog post template with the post data
    return render_template('blog_post.html', user=user, post=new_post, comments=new_comments)


@blogs.route('/blog/<int:post_id>/comment', methods=['POST'])
@authenticate
def add_comment(user, post_id):
    content = request.form.get('content')
    query = text(f"INSERT INTO comments (content, date, user_id, blog_id) VALUES ('{content}', '{render_time()}','{user.id}','{post_id}')")
    db.session.execute(query)
    db.session.commit()

    flash('Comment Posted!', category='success')
    current_app.logger.info(f'COMMENT_ADDED: user_id:{user.id} post_id:{post_id}')
    # Redirect back to the blog post page
    return redirect(f"/blog/{post_id}")


@blogs.route('/comment', methods=['DELETE'])
def delete_comment():
    id = request.json['comment_id']
    query = text(f"DELETE FROM comments WHERE id='{id}'")
    db.session.execute(query)
    db.session.commit()

    flash('Comment Deleted!', category='success')
    current_app.logger.info(f'COMMENT_DELETED: comment_id:{id}')

    return jsonify({'message': 'Comment deleted successfully'})