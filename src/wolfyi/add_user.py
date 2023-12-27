import argparse
import getpass

from wolfyi.application.models import User


def main():
    p = argparse.ArgumentParser()
    p.add_argument('email')
    p.add_argument('password', nargs='?')
    p.add_argument('-a', '--admin', action='store_true')
    args = p.parse_args()

    User.create(
        email=args.email,
        password=args.password or getpass.getpass(),
        is_admin=args.admin,
    )

    print('Success')


if __name__ == "__main__":
    main()
