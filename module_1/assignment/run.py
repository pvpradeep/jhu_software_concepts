from myPage import create_app

app = create_app()

if __name__ == "__main__":
    # Run app on localhost port 8080 with debug enabled if desired
    app.run(host='127.0.0.1', port=8080, debug=True)
