from datetime import datetime
from flask import Blueprint, render_template, request, flash, jsonify, redirect, send_from_directory, session, send_file, current_app
from . import db
from .auth import authenticate
from .views import render_time
import os
from sqlalchemy import text

support = Blueprint('support', __name__)

# Support-Ticket
@support.route('/support', methods=['GET'])
@authenticate
def submit_support_request(user):
    return render_template('open_ticket.html', user=user)


@support.route('/open-ticket', methods=['GET', 'POST'])
@authenticate
def open_ticket(user):
    if request.method == 'POST':
        # Process the form submission and create a new ticket in the database
        # Retrieve the necessary information from the form data
        title = request.form.get('title')
        content = request.form.get('content')

        # Save the ticket to the database
        query = text(
            f"INSERT INTO tickets (title, user_id, content, date) VALUES ('{title}', '{user.id}', '{content}', '{render_time()}')")
        db.session.execute(query)
        db.session.commit()

        current_app.logger.info(f'TICKET_POSTED: user_id:{user.id} title:{title}')
        # Redirect the user to their ticket list page or ticket details page
    query = text(f"SELECT * FROM tickets WHERE user_id='{user.id}'")
    user_tickets = db.session.execute(query).fetchall()

    # Render the form template for opening a ticket
    return render_template('open_ticket.html', user=user, user_tickets=user_tickets)


@support.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@authenticate
def view_ticket(user, ticket_id):
    if request.method == 'POST':
        # Process the form submission and add a new message to the ticket
        # Retrieve the necessary information from the form data
        content = request.form.get('message')
        # Save the message to the ticket in the database
        query = text(f"INSERT INTO ticket_messages (ticket_id, content, user_id, date) VALUES ('{ticket_id}', '{content}','{user.id}', '{render_time()}')")
        db.session.execute(query)
        db.session.commit()

        current_app.logger.info(f'TICKET_MESSAGE: user_id:{user.id} ticket_id:{ticket_id}')
        # Redirect the user back to the ticket page to view the updated ticket and messages
    query = text(f"SELECT * FROM tickets WHERE id ='{ticket_id}'")
    ticket = db.session.execute(query).first()

    query = text(f"SELECT * FROM users WHERE id ='{ticket.user_id}'")
    tmp_user = db.session.execute(query).first()
    owner_username = tmp_user.username
    # Collect all Messages
    messages = []
    query = text(f"SELECT * FROM ticket_messages WHERE ticket_id = '{ticket.id}'")
    ticket_messages = db.session.execute(query).fetchall()
    for message in ticket_messages:
        query = text(f"SELECT username FROM users WHERE id='{message.user_id}'")
        tmp_user = db.session.execute(query).first()
        username = tmp_user.username
        new_message = {
            'id': message.id,
            'ticket_id': message.ticket_id,
            'content': message.content,
            'date': message.date,
            'user_id': message.user_id,
            'username': username
        }
        messages.append(new_message)
    return render_template('ticket.html', user=user, ticket=ticket, ticket_messages=messages, username=owner_username)


@support.route('/admin/tickets')
@authenticate
def admin_tickets(user):
    query = text(f"SELECT * FROM tickets")
    tickets = db.session.execute(query).fetchall()
    username_tickets = []
    for ticket in tickets:
        new_ticket = ticket_username(ticket.id)
        username_tickets.append(new_ticket)
    return render_template('admin_tickets.html', user=user, tickets=username_tickets)


# Route for handling ticket deletion
@support.route("/admin/tickets/delete/<int:ticket_id>", methods=["POST"])
def delete_ticket(ticket_id):
    query = text(f"DELETE FROM tickets WHERE id='{ticket_id}'")
    db.session.execute(query)
    db.session.commit()
    current_app.logger.info(f'TICKET_DELETED: ticket_id:{ticket_id}')

    # Redirect to the admin tickets page after deletion
    return redirect("/admin/tickets")


# Route for handling ticket status update
@support.route("/admin/tickets/update-status/<int:ticket_id>/<status>", methods=["POST"])
def update_ticket_status(ticket_id, status):
    query = text(f"UPDATE tickets SET status = '{status}' WHERE id = '{ticket_id}'")
    db.session.execute(query)
    db.session.commit()
    current_app.logger.info(f'USER_UPDATED: ticket_id:{ticket_id} status:{status}')

    # Redirect to the admin tickets page after updating the status
    return redirect("/admin/tickets")


def ticket_username(ticket_id):
    query = text(f"SELECT * FROM tickets WHERE id = '{ticket_id}'")
    ticket = db.session.execute(query).first()
    query = text(f"SELECT * FROM users WHERE id = '{ticket.user_id}'")
    user = db.session.execute(query).first()
    new_ticket = {
        'id': ticket.id,
        'title': ticket.title,
        'content': ticket.content,
        'status': ticket.status,
        'date': ticket.date,
        'user_id': ticket.user_id,
        'username': user.username,
    }
    return new_ticket
