from website import create_app

app = create_app()

app.jinja_env.autoescape = False
if __name__ == '__main__':
    app.run(debug=True)
