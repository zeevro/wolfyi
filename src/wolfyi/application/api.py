import secrets
from datetime import datetime

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from . import db
from .models import URL, User, Visit
from .utils import ApiError, api_endpoint, normalize_url_input


bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/')
@login_required
def static_page():
    return render_template('js-app.html')


@bp.route('/index')
@login_required
@api_endpoint
def index():
    urls = (db.session.query(URL,
                             func.count(Visit.id))
                      .filter(URL.user_id == current_user.id)
                      .outerjoin(Visit)
                      .group_by(URL.id)
                      .order_by(URL.created.desc())
                      .all())

    return {
        'user': {
            'email': current_user.email,
            'created': current_user.created.timestamp(),
        },
        'urls': [
            {
                'id': u.id,
                'url': u.url,
                'created': u.created.timestamp(),
                'visits': v,
            }
            for u, v
            in urls
        ],
    }


@bp.route('/add', methods=['POST'])
@login_required
@api_endpoint
def add_url():
    url = normalize_url_input(request.json['url'])

    if not url:
        raise ApiError('Empty url')

    old_url = URL.query.filter(URL.user_id == current_user.id, URL.url == url).first()
    if old_url is not None:
        raise ApiError('Already taken', id=old_url.id)

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

    return {
        'id': new_url.id,
        'url': new_url.url,
        'created': new_url.created.timestamp(),
    }


@bp.route('/edit', methods=['POST'])
@login_required
@api_endpoint
def edit_url():
    url = URL.query.filter(URL.id == request.json['id'], URL.user_id == current_user.id).first_or_404()

    new_url = normalize_url_input(request.json['url'])

    if not new_url:
        raise ApiError('Empty url')

    taken = URL.query.filter(URL.user_id == current_user.id, URL.url == new_url).first()
    if taken:
        db.session.rollback()
        raise ApiError('Already taken', id=taken.id)

    url.url = new_url
    db.session.commit()

    return {
        'url': url.url,
    }


@bp.route('/delete', methods=['POST'])
@login_required
@api_endpoint
def delete_url():
    url = URL.query.filter(URL.id == request.json['id'], URL.user_id == current_user.id).first_or_404()
    db.session.delete(url)
    db.session.commit()


@bp.route('/account', methods=['POST'])
@login_required
@api_endpoint
def account():
    if not request.json['password']:
        raise ApiError('Invalid password')

    if request.json['password'] == request.json['old_password']:
        raise ApiError('Same as old password')

    if not current_user.check_password(request.json['old_password']):
        raise ApiError('Old password is wrong')

    user = db.session.query(User).get(current_user.id)
    user.set_password(request.json['password'])
    db.session.commit()
