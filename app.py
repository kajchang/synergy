from flask import Flask, redirect, request, render_template, send_from_directory, session, url_for
from flask_session import RedisSessionInterface
from redis import from_url

from studentvue import StudentVue
from studentvue.models import Class

import os
import json

app = Flask(__name__)
SESSION_TYPE = 'redis'
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
app.session_interface = RedisSessionInterface(from_url(REDIS_URL), 'session:')


@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)


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
        return render_template('home.html', **session.get('StudentVue').__dict__)
    else:
        return redirect(url_for('index'))


@app.route('/grades', methods=['GET'])
def grades():
    if session.get('StudentVue'):
        sv = session.get('StudentVue')

        def dump_class(class_):
            res = class_.__dict__
            res['teacher'] = res['teacher'].__dict__
            return json.dumps(res)

        return render_template('grades.html',
                               schedule=sv.get_schedule(), grade_book=sv.get_grade_book(), dump=dump_class)
    else:
        return redirect(url_for('index'))


@app.route('/course_history', methods=['GET'])
def course_history():
    if session.get('StudentVue'):
        sv = session.get('StudentVue')
        return render_template('course_history.html', course_history=sv.get_course_history())
    else:
        return redirect(url_for('index'))


@app.route('/class_info', methods=['GET'])
def class_info():
    if session.get('StudentVue'):
        if request.args.get('class'):
            try:
                sv = session.get('StudentVue')
                class_ = Class(**json.loads(request.args.get('class')))
                ctx = {}
                ctx.update(class_.__dict__)
                ctx.update(sv.get_class_info(class_))
                return render_template('class_info.html', **ctx)
            except Exception as e:
                print(e)
                return redirect(url_for('grades'))
        else:
            return redirect(url_for('grades'))
    else:
        return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('StudentVue')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
