from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import random
import string
from datetime import datetime, timedelta, timezone
from io import BytesIO


app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)


def init_db():
    os.system('rm app.db')
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reviews
                      (id INTEGER PRIMARY KEY, 
                      book TEXT NOT NULL,
                      content TEXT NOT NULL, 
                      review_created_at timestamp NOT NULL);''')
    conn.commit()
    conn.close()
    

def extract_reviews():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reviews ORDER BY review_created_at DESC;')
    a = cursor.fetchall()
    conn.close()
    return a


def new_review(bookname, content):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO reviews (book, content, review_created_at)
                      VALUES (?, ?, DATETIME('now')) ON CONFLICT DO NOTHING;''', 
                      (bookname, content))
    conn.commit()
    cursor.execute('SELECT * FROM reviews WHERE book = ? AND content = ? ORDER BY id DESC;', (bookname, content,))
    a = cursor.fetchone()
    conn.close()
    return a


@app.route('/reviews', methods=['GET'])
def get_reviews():
    tmp = extract_reviews()
    if len(tmp) > 0:
        return jsonify({'reviews':tmp}), 200
    else:
        return jsonify({'reviews':[]}), 200


@app.route('/review', methods=['POST'])
def add_review():
    data = request.json
    if not data.get('book') or not data.get('content'):
        return jsonify({'message': 'book and content fields are required'}), 400
    tmp = new_review(data['book'], data['content'])
    return jsonify({'reviews': tmp}), 201


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5000)), debug=False)
