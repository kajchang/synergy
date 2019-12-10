from flask import Flask, redirect, request, render_template, session, url_for
from flask_session import RedisSessionInterface
from redis import Redis

from studentvue import StudentVue

import os

app = Flask(__name__)
SESSION_TYPE = 'redis'
REDIS_URL = os.environ.get('REDIS_URL', 'redis://h:localhost:6379')
app.session_interface = RedisSessionInterface(Redis(host=REDIS_URL.split(':')[2], port=REDIS_URL.split(':')[3]),
                                              'session:')


@app.route('/', methods=['GET'])
def index():
    if session.get('sv_cookie'):
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

    session['sv_cookie'] = sv.session.cookies
    session['name'] = sv.name
    session['student_id'] = sv.id_
    return redirect(url_for('home'))


@app.route('/home', methods=['GET'])
def home():
    if session.get('sv_cookie'):
        return render_template('home.html', **session)
    else:
        return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
def logout():
    for item in list(session.keys()):
        session.pop(item)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
