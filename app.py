
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy  # add
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # add
db = SQLAlchemy(app)


class cached_db(dict):

    def __init__(self):
        self = dict()

    def if_exists(self, key):
        return key in self

    def add(self, key, value):
        self[key] = value

    def get_value(self, key):
        return self[key]['value']

    def delete(self, key):
        if not self.if_exists(key):
            return "key not present"
        del self[key]
        return "deleted"


cache = cached_db()

class redis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(80), nullable=False)
    expiry = db.Column(db.DateTime, nullable=False,
                       default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/set', methods=['POST'])
def set_key_value():
    req = request.get_json()
    key = req['key']
    value = req['value']

    obj = redis(key=key, value=value)
    try:
        db.session.add(obj)
        db.session.commit()
        return "saved"
    except:
        return "There was a problem adding key"


@app.route('/get', methods=['GET'])
def get_key_value():
    req = request.args.get('key')

    return cache.get_value(req)


@app.route('/delete', methods=['GET'])
def delete_key_value():
    req = request.args.get('key')

    return cache.delete(req)


def init():
    hash_map = redis.query.all()
    for key_value in hash_map:
        cache.add(key_value.as_dict()['key'], key_value.as_dict())


init()

if __name__ == '__main__':
    app.run(debug=True)
