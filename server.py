import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Flask, request, jsonify, make_response, send_from_directory, render_template_string

from errors import TokenNotFoundError, InvalidTokenError
from models import db, User, LoginHistory

from hashlib import sha256

app = Flask(__name__)
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'JyFZ8Ia59DZtoneeG4g'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://localhost:5432/ycp?user=postgres&password' \
                                        '=supersecretpassword'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


def authenticate(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            token = request.args.get('token')
            if not token:
                return make_response(jsonify({'success': False, 'message': 'Token is missing!'}), 401)
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except InvalidTokenError:
            return make_response(jsonify({'success': False, 'message': 'Invalid token'}), 403)
        return func(*args, **kwargs)

    return decorated


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'jwt.ico')


@app.route("/")
def home():
    return render_template_string(
        """
            <head>
                <link rel="shortcut icon" href="{{ url_for('static', filename='jwt.ico') }}">
                <title> JWT History </title>
            </head>
            <h1>Welcome to JWT History Server!</h1>
            <h3>If you see this, it means the program is running~</h3>
        """
    )


@app.route("/register", methods=['POST'])
def register():
    request_json = dict(request.get_json(force=True))
    username, password = request_json.get("username"), request_json.get("password")
    existing_user_name = User.query.filter_by(username=username).first()

    if existing_user_name:
        return make_response(jsonify({'success': False, 'message': 'Username already exists!'}), 400)

    hashed_password = sha256(password.encode('utf-8')).hexdigest()
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return make_response(jsonify({'success': True, 'message': 'User has successfully been registered'}), 201)


@app.route("/login", methods=['POST'])
def login():
    request_json = dict(request.get_json(force=True))
    username, password = request_json.get("username"), request_json.get("password")
    existing_user = User.query.filter_by(username=username).first()
    hashed_password = sha256(password.encode('utf-8')).hexdigest()

    if (not existing_user) or (existing_user.password != hashed_password):
        return make_response(jsonify({'success': False, 'message': 'You have inputted the wrong username/password'}),
                             401)

    new_login_entry = LoginHistory(username=username)
    token = jwt.encode(
        {'username': existing_user.username, 'exp': datetime.utcnow() + timedelta(minutes=30)},
        app.config['SECRET_KEY'])
    db.session.add(new_login_entry)
    db.session.commit()
    return make_response(jsonify({'success': True, 'data': {'token': token}}),
                         201)


@app.route("/login-history")
@authenticate
def login_history():
    page = dict(request.get_json()).get('page', 1)
    username = jwt.decode(request.args.get('token'), app.config['SECRET_KEY'], algorithms=['HS256']).get('username')
    per_page = 10
    login_history_paginated = LoginHistory.query.filter_by(username=username).order_by(
        LoginHistory.time.desc()).paginate(page, per_page,
                                           error_out=False).items
    login_history_response = [{'username': entry.username, 'time': entry.time} for entry in login_history_paginated]
    return make_response(jsonify({'success': True, 'data': {'logins': login_history_response}}),
                         201)


if __name__ == '__main__':
    app.run()
