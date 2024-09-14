from flask import Flask, request, render_template, make_response
import os
import random
import uuid


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.jinja_options = {"autoescape": False}
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

@app.after_request
def apply_csp(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-eval' ajax.googleapis.com; "
    )
    return response



@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        resp = make_response(render_template('index.html'))
        if not request.cookies.get('uid'):
            resp.set_cookie('uid', uuid.uuid4().hex)
        return resp
    if request.method == 'POST':
        got_search = request.form.get('search')
        resp = make_response(render_template('index.html', search=got_search, r=random.randint(5,20) if got_search else 0))
        if not request.cookies.get('uid'):
            resp.set_cookie('uid', uuid.uuid4().hex)
        return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5000)), debug=True)
