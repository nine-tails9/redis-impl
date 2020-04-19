from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy  # add
from datetime import datetime, timedelta
from sortedcontainers import SortedDict

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # add
db = SQLAlchemy(app)

# model
class redis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80), nullable=False)
    expiry = db.Column(db.DateTime, nullable=False,
                       default=timedelta(hours=9999) + datetime.utcnow())
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# memcache

class cached_db(dict):

    def __init__(self):
        self = dict()

    def if_exists(self, key):
        if self[key]['expiry'] < datetime.utcnow():
            self.delete(key)
        return key in self and self[key]['expiry'] >= datetime.utcnow()

    def add(self, key, value):
        self[key] = value

    def get_value(self, key):
        if not self.if_exists(key):
            return "Key doesnot exists"
        return self[key]['value']

    def delete(self, key):
        if not self.if_exists(key):
            return "key not present"
        del self[key]
        redis.query.filter_by(key=key, type="unsorted").delete()
        db.session.commit()
        return "deleted"


class sorted_cached_db:

    def __init__(self):
        self.sorted_map = SortedDict()

    def if_exists(self, key):
        return key in self.sorted_map

    def add(self, key, value):
        self.sorted_map[key] = value

    def delete(self, key):
        if not self.if_exists(key):
            return "key not present"
        del self.sorted_map[key]
        redis.query.filter_by(key=key, type="sorted").delete()
        db.session.commit()
        return "deleted"

    def find_rank(self, key):
        if not self.if_exists(key):
            return "does'not exists"
        return jsonify(self.sorted_map.keys()[:])

    def get_range(self, start, end):
        n = len(self.sorted_map)
        start = (n + start) % n
        end = (n + end) % n + 1
        return jsonify([self.sorted_map[key]['value'] for key in self.sorted_map.islice(start, end)])

# routes

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/set', methods=['POST'])
def set_key_value():
    req = request.get_json()
    key = req['key']
    value = req['value']

    obj = redis(key=key, value=value, type="unsorted")
    try:
        db.session.add(obj)
        db.session.commit()
        cache.add(key, obj.as_dict())
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


@app.route('/set-expiry', methods=['POST'])
def set_key_expiry():
    req = request.get_json()
    key = req['key']
    expiry = int(req['expiry'])
    if not cache.if_exists(key):
        return "key not present"
    obj = redis.query.filter_by(key=key).first()
    obj.expiry = timedelta(seconds=expiry) + datetime.utcnow()
    db.session.commit()
    cache.add(key, obj.as_dict())
    return "expiry set"


@app.route('/zadd', methods=['POST'])
def zadd_key_value():
    req = request.get_json()
    key = req['key']
    value = req['value']
    obj = redis(key=key, value=value, type="sorted")
    db.session.add(obj)
    db.session.commit()
    sorted_cache.add(key, obj.as_dict())
    return "saved"



@app.route('/zrank', methods=['GET'])
def get_key_rank():
    req = request.args.get('key')
    return sorted_cache.find_rank(req)


@app.route('/zrange', methods=['GET'])
def get_key_range():
    start = request.args.get('start')
    end = request.args.get('end')
    return sorted_cache.get_range(int(start), int(end))

#################################################################

cache = cached_db()
sorted_cache = sorted_cached_db()

def init():
    rows = redis.query.all()
    for key_value in rows:
        print(key_value.as_dict())
        if key_value.as_dict()['type'] == "unsorted":
            cache.add(key_value.as_dict()['key'], key_value.as_dict())
        else:
            sorted_cache.add(key_value.as_dict()['key'], key_value.as_dict())


init()

if __name__ == '__main__':
    app.run(debug=True)
