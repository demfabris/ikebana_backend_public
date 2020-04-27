# run.py

from app import instance

app = instance()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
