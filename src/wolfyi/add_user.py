import argparse
import getpass

from wolfyi.application import create_app, db
from wolfyi.application.models import User


def main():
    p = argparse.ArgumentParser()
    p.add_argument('email')
    p.add_argument('password', nargs='?')
    p.add_argument('-a', '--admin', action='store_true')
    args = p.parse_args()

    app = create_app()

    new_user = User(
        email=args.email,
        password=args.password or getpass.getpass(),
        is_admin=args.admin,
    )

    with app.app_context():
        db.session.add(new_user)
        db.session.commit()


if __name__ == "__main__":
    main()
