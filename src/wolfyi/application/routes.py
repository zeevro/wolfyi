import secrets
from datetime import datetime

from flask import abort
from flask import current_app as app
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from . import db
from .models import URL, User
from .utils import normalize_url_input


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


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_url():
    url = normalize_url_input(request.values['url'])

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


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_url():
    url = URL.query.filter(URL.id == request.values['id'], URL.user_id == current_user.id).first_or_404()
    if request.method == 'GET':
        return render_template('edit.html', url=url)

    new_url = normalize_url_input(request.form['url'])

    taken = URL.query.filter(URL.user_id == current_user.id, URL.url == new_url).first()
    if taken:
        db.session.rollback()
        return render_template('message.html', message=f'URL already taken by { request.host_url }{ taken.id }')

    url.url = new_url
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/delete')
@login_required
def delete_url():
    url = URL.query.filter(URL.id == request.args['id'], URL.user_id == current_user.id).first_or_404()
    if not request.args.get('sure', None):
        return render_template('delete.html', url=url)
    db.session.delete(url)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template('message.html', message='Not implemented yet')


@app.route('/<regex("[A-Za-z0-9_-]{6,8}"):slug>')
def redirect_to_url(slug):
    url = URL.query.filter(URL.id == slug).first()
    if url is None:
        return abort(404)
    return redirect(url.url)
