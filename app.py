from flask import Flask, redirect, request, render_template, session, url_for
from flask_session import Session

from studentvue import StudentVue

import os

app = Flask(__name__)
SESSION_TYPE = 'redis'
REDIS_URL = os.environ.get('REDIS_URL', None)
app.config.from_object(__name__)
Session(app)


@app.route('/', methods=['GET'])
def index():
    if session.get('StudentVue'):
        return redirect(url_for('home'))
    else:
        return render_template('index.html')


@app.route('/', methods=['POST'])
def authenticate():
    try:
        sv = StudentVue(request.form.get('username'), request.form.get('password'), 'portal.sfusd.edu')
    except ValueError:
        return render_template('index.html', error='Incorrect Username or Password.')
    except Exception:
        return render_template('index.html', error='Unexpected Error.')

    session['StudentVue'] = sv
    return redirect(url_for('home'))


@app.route('/home', methods=['GET'])
def home():
    if session.get('StudentVue'):
        return render_template('home.html', StudentVue=session.get('StudentVue'))
    else:
        return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('StudentVue')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
