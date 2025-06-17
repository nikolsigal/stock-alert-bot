from server import app

if __name__ == "__main__":
    from server import send_update
    send_update()
    app.run(host='0.0.0.0', port=8080)
