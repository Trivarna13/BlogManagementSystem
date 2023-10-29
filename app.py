from website import create_app

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        from website import db
        db.create_all()

    app.run(debug=False,host='0.0.0.0')
