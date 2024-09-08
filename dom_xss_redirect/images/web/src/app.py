from flask import Flask, request, render_template
import os
import random


app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        got_search = request.form.get('search')
        return render_template('index.html', search=got_search, r=random.randint(5,20) if got_search else 0)

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'GET':
        return render_template('survey.html')
    if request.method == 'POST':
        got_name = request.form.get('name')
        got_age = request.form.get('age')
        got_city = request.form.get('city')
        return render_template('survey.html', name=got_name, age=got_age, city=got_city)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5000)), debug=True)
