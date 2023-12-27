import time

from flask import current_app as app
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from peewee import fn
from playhouse.flask_utils import get_object_or_404
from pyisemail import is_email

from .models import URL, Invite, User, Visit, database
from .utils import normalize_url_input


@app.route('/register', methods=['GET', 'POST'])
def register():
    invite_code = request.values.get('invite', '')

    if request.method == 'GET':
        return render_template('register.html', invite_code=invite_code)

    invite: Invite = Invite.get_by_id(invite_code)

    if invite is None:
        return render_template('register.html', invite_code=invite_code, error='Invalid invite code')

    email_diagnosis = is_email(request.form['email'], check_dns=True, diagnose=True)
    if email_diagnosis.code:
        return render_template('register.html', invite_code=invite_code, error=f'Invalid email ({email_diagnosis.message})')

    if User.filter(User.email == request.form['email']).count():
        return render_template('register.html', invite_code=invite_code, error='Email already taken')

    if not request.form['password']:
        return render_template('register.html', invite_code=invite_code, error='Invalid password')

    if request.form['password'] != request.form['password2']:
        return render_template('register.html', invite_code=invite_code, error='Passwords did not match')

    with database.atomic():
        new_user: User = User.create(
            email=request.form['email'],
            password=request.form['password'],
        )
        invite.update(used=time.time(), used_by=new_user)

    login_user(new_user)

    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('login.html')

    user = User.get_or_none(User.email == request.form['email'])
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
    current_user.urls = list(current_user.urls.select(URL, fn.COUNT(Visit.id).alias('visit_count')).left_outer_join(Visit).group_by(Visit.url_id).order_by(URL.created.desc()))
    return render_template('index.html')


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_url():
    url = normalize_url_input(request.values['url'])

    if not url:
        return redirect(url_for('index'))

    url_obj = URL.filter(URL.user == current_user, URL.url == url).first()
    while url_obj is None:
        try:
            url_obj = URL.create(user=current_user, url=url)
        except Exception as e:
            print('ERROR!', e)

    return redirect(url_for('index', copy=url_obj.id))


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_url():
    url = get_object_or_404(URL.filter(URL.id == request.values['id'], URL.user == current_user))
    if request.method == 'GET':
        return render_template('edit.html', url=url)

    new_url = normalize_url_input(request.form['url'])

    if not new_url:
        return render_template('edit.html', url=url, error='Empty URL')

    taken = URL.filter(URL.user == current_user, URL.url == new_url).first()
    if taken:
        db.session.rollback()
        return render_template('edit.html', url=url, error=f'URL already taken by { request.host_url }{ taken.id }')

    url.url = new_url
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/delete')
@login_required
def delete_url():
    url = URL.filter(URL.id == request.args['id'], URL.user == current_user).first_or_404()
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
    url = get_object_or_404(URL, slug)

    url.add_visit()

    return redirect(url.url)
