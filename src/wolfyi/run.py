from wolfyi.application import create_app


def main():
    app = create_app(echo=True)
    app.run('0.0.0.0', 5000, debug=True)


if __name__ == "__main__":
    main()
