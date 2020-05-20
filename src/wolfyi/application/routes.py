import secrets
from datetime import datetime

from flask import abort
from flask import current_app as app
from flask import redirect, render_template, request, url_for, session
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from . import db
from .models import User, URL


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return 'Not yet implemented.<br /><a href="/">Go home</a>'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('login.html')

    user = User.query.filter(User.email == request.form['email']).first()

    if user is None or not user.check_password(request.form['password']):
        return 'Wrong email or password'

    login_user(user, remember=True)

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
@login_required
def add_url():
    url = request.form['url']
    if '://' not in url:
        url = 'http://' + url

    old_url = URL.query.filter(URL.user_id == current_user.id, URL.url == url).first()
    if old_url is not None:
        return render_template('created.html', url=old_url)

    new_url = URL(
        user_id=current_user.id,
        url=url,
        created=datetime.utcnow(),
    )

    while 1:
        try:
            new_url.id = secrets.token_urlsafe()[:6]
            db.session.add(new_url)
            db.session.commit()
        except IntegrityError as e:
            print('ERROR!', e)
            continue

        break

    return render_template('created.html', url=new_url)
    return f'{new_url.id} &rarr; {new_url.url}'


@app.route('/<regex("[A-Za-z0-9_-]{6,8}"):slug>')
def redirect_to_url(slug):
    url = URL.query.filter(URL.id == slug).first()
    if url is None:
        return abort(404)
    return redirect(url.url)
