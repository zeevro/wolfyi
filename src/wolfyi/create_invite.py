from wolfyi.application.models import Invite


def main():
    print(f'https://wol.fyi/register?invite={Invite.create().id}')


if __name__ == '__main__':
    main()
