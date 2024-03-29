import secrets
from datetime import datetime

from flask import current_app as app
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from . import db
from .models import Invite, URL, User, Visit
from .utils import is_valid_email, normalize_url_input


@app.route('/register', methods=['GET', 'POST'])
def register():
    invite_code = request.values.get('invite', '')

    if request.method == 'GET':
        return render_template('register.html', invite_code=invite_code)

    invite = Invite.query.get(invite_code)

    if invite is None:
        return render_template('register.html', invite_code=invite_code, error='Invalid invite code')

    if not is_valid_email(request.form['email']):
        return render_template('register.html', invite_code=invite_code, error='Invalid email')

    if User.query.filter(User.email == request.form['email']).count():
        return render_template('register.html', invite_code=invite_code, error='Email already taken')

    if not request.form['password']:
        return render_template('register.html', invite_code=invite_code, error='Invalid password')

    if request.form['password'] != request.form['password2']:
        return render_template('register.html', invite_code=invite_code, error='Passwords did not match')

    new_user = User(
        email=request.form['email'],
        password=request.form['password'],
    )
    db.session.add(new_user)
    db.session.flush()

    invite.used = datetime.utcnow()
    invite.used_by = new_user.id

    db.session.commit()

    login_user(new_user)

    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('login.html')

    user = User.query.filter(User.email == request.form['email']).first()

    if user is None or not user.check_password(request.form['password']):
        return render_template('login.html', error='Wrong email or password')

    login_user(user, remember=True)

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    visits = dict(db.session.query(URL.id,
                                   func.count(Visit.id))
                            .filter(URL.user_id == current_user.id)
                            .outerjoin(Visit)
                            .group_by(URL.id)
                            .all())
    return render_template('index.html', visits=visits)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_url():
    url = normalize_url_input(request.values['url'])

    if not url:
        return redirect(url_for('index'))

    old_url = URL.query.filter(URL.user_id == current_user.id, URL.url == url).first()
    if old_url is not None:
        return redirect(url_for('index', copy=old_url.id))

    new_url = URL(
        user_id=current_user.id,
        url=url,
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

    return redirect(url_for('index', copy=new_url.id))


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_url():
    url = URL.query.filter(URL.id == request.values['id'], URL.user_id == current_user.id).first_or_404()
    if request.method == 'GET':
        return render_template('edit.html', url=url)

    new_url = normalize_url_input(request.form['url'])

    if not new_url:
        return render_template('edit.html', url=url, error=f'Empty URL')

    taken = URL.query.filter(URL.user_id == current_user.id, URL.url == new_url).first()
    if taken:
        db.session.rollback()
        return render_template('edit.html', url=url, error=f'URL already taken by { request.host_url }{ taken.id }')

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
    return redirect(url_for('index', message=f'{ request.host_url }{ url.id } deleted.'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'GET':
        return render_template('account.html')

    if not request.form['password']:
        return render_template('account.html', error='Invalid password')

    if request.form['password'] == request.form['old_password']:
        return render_template('account.html', error='Same as old password')

    if request.form['password'] != request.form['password2']:
        return render_template('account.html', error='Passwords did not match')

    if not current_user.check_password(request.form['old_password']):
        return render_template('account.html', error='Old password is wrong')

    user = db.session.query(User).get(current_user.id)
    user.set_password(request.form['password'])
    db.session.commit()

    return render_template('account.html', message='Password changed')


@app.route('/<regex("[A-Za-z0-9_-]{6,8}"):slug>')
def redirect_to_url(slug):
    url = URL.query.get_or_404(slug)

    url.add_visit()

    return redirect(url.url)
