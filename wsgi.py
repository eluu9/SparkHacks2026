from app import create_app

app = create_app()

if __name__ == "__main__":
    print("server starting")
    app.run(host='0.0.0.0', port=5000)