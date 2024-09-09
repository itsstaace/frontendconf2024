from flask import Flask, request, session, render_template, jsonify
import sqlite3
import bcrypt
import os
import random
import string
from datetime import datetime, timedelta, timezone
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.jinja_options = {"autoescape": False}
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


def init_db():
    os.system('rm app.db')
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY, 
                      username TEXT NOT NULL,
                      fio TEXT,
                      password_hash TEXT NOT NULL, 
                      user_created_at timestamp)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments
                    (id INTEGER PRIMARY KEY, amount REAL NOT NULL, comment TEXT, user_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id));''')
    # cursor.execute('''INSERT INTO payments (amount, comment, user_id) VALUES (?, ?, (SELECT id FROM users WHERE username='admin')) ON CONFLICT DO
    #                 NOTHING;''', (-100, flag))
    conn.commit()
    conn.close()


def check_username(username):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row is not None:
        return False
    else:
        return True


def check_user_exists(user_id):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    if row and row[0]:
        return row[0]
    else:
        return False


def register_user(username, password, fio):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users (username, password_hash, user_created_at, fio) VALUES 
                            (?, ?, DATETIME(\'now\'), ?) ON CONFLICT DO NOTHING;''',
                   (username, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()), fio))
    conn.commit()
    conn.close()


def check_creds(username, password):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username, ))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    if row and row[0] and row[2] and bcrypt.checkpw(password.encode('utf-8'), row[2]):
        return row[0]
    return False
    

def get_payments(user_id):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, amount, comment FROM payments WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if row and row[0]:
        return jsonify({"id": row[0], "amount": row[1], "comment": row[2]})
    else:
        return False


def get_name(user_id):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT fio FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    if row and row[0]:
        return jsonify({"name": row[0]})
    else:
        return False


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/user')
def profile():
    user_id = session.get('user_id')
    token_expires = session.get('expires')
    if not user_id or not token_expires:
        return render_template('login.html')
    if token_expires and datetime.now(timezone.utc) >= token_expires:
        return render_template('login.html')
    else:
        if user_id:
            username = check_user_exists(user_id)
            if username:
                return render_template('profile.html', username=username, user_id=user_id)
        return render_template('login.html')


@app.route('/api/name', methods=['POST'])
def fio():
    sess_id = session.get('user_id')
    token_expires = session.get('expires')
    if not sess_id or not token_expires:
        return jsonify({"error": "Нет доступа"}), 401
    if token_expires and datetime.now(timezone.utc) >= token_expires:
        return jsonify({"error": "Время действия токена истекло"}), 401
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Нет данных"}), 400
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "Нет данных"}), 400
    else:
        p_data = get_name(user_id)
        if p_data:
            return p_data, 200
        else:
            return jsonify({"error": "Нет данных"}), 200


@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        got_username = request.form.get('username')
        got_password = request.form.get('password')

        if not got_username:
            return render_template('login.html', error="Не заполнено имя пользователя")
        if not got_password:
            return render_template('login.html', error="Не заполнен пароль")

        if got_username and got_password:
            user_id = check_creds(got_username, got_password)
            if user_id:
                session['user_id'] = user_id
                session['expires'] = datetime.now(timezone.utc) + timedelta(hours=24)
                return render_template('profile.html', username=got_username, user_id=user_id) 
            else:
                return render_template('login.html', error="Неверное имя пользователя или пароль.")
        else:
            return render_template('login.html', error="Неверное имя пользователя или пароль.")

    else:
        return render_template('login.html')


@app.route('/api/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        fio = request.form.get('fio')
        password = request.form.get('password')
        if not username:
            return render_template('register.html', error="Не заполнено имя пользователя")
        if not password:
            return render_template('register.html', error="Не заполнен пароль")
        if not fio:
            return render_template('register.html', error="Не заполнены ФИО")

        if check_username(username):
            register_user(username, password, fio)
            return render_template('reg_success.html')
        else:
            return render_template('register.html', error="Пользователь с указанным именем уже существует.")
    else:
        return render_template('register.html')

# @app.route('/api/payments', methods=['POST'])
# def payments():
#     sess_id = session.get('user_id')
#     token_expires = session.get('expires')
#     if not sess_id or not token_expires:
#         return jsonify({"error": "Нет доступа"}), 401
#     if token_expires and datetime.now(timezone.utc) >= token_expires:
#         return jsonify({"error": "Время действия токена истекло"}), 401
#     data = request.get_json()
#     if data is None:
#         return jsonify({"error": "Нет данных"}), 400
#     user_id = sess_id
#     if not user_id:
#         return jsonify({"error": "Нет данных"}), 400
#     else:
#         p_data = get_payments(user_id)
#         if p_data:
#             return p_data, 200
#         else:
#             return jsonify({"error": "Нет платежей"}), 200
        

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5000)), debug=False)
