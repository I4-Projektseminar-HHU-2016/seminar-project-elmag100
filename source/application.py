import os
import sqlite3
from flask import Flask, render_template, g, flash

app = Flask(__name__)

app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'restaurant.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

DATABASE = 'restaurant.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# Routes

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT * FROM user')
    users = cur.fetchall()
    return render_template('index.html', users=users, length=len(users))

@app.route('/user/<int:user_id>')
def user(user_id):
    db = get_db()
    cur = db.execute('SELECT * FROM user WHERE id = ?', (user_id,))
    users = cur.fetchall()
    return render_template('user.html', user = users[0])
