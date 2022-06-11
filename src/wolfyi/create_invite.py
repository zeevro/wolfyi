import secrets
from datetime import datetime

from wolfyi.application import create_app, db
from wolfyi.application.models import Invite


def main():
    app = create_app()

    new_invite = Invite()

    with app.app_context():
        db.session.add(new_invite)
        db.session.commit()

        print(f'https://wol.fyi/register?invite={new_invite.id}')


if __name__ == "__main__":
    main()
