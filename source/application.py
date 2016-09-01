#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
import sqlite3
import unicodecsv as csv
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
    users = query_db('SELECT * FROM user')
    return render_template('index.html', users=users, length=len(users))

@app.route('/user/<int:user_id>')
def user(user_id):
    user = query_db('SELECT * FROM user WHERE id = ?', (user_id,), True)
    return render_template('user.html', user = user)
    
@app.route('/restaurants', defaults={'zip': 0})
@app.route('/restaurants/<int:zip>')
def restaurants(zip=0):
    if zip == 0:
        restaurants = query_db('SELECT * FROM restaurant')
    else:
        restaurants = query_db('SELECT * FROM restaurant WHERE zip = ?', (zip,))
    return render_template('restaurants.html', restaurants=restaurants, result_count=len(restaurants))

@app.route('/restaurants/keyword/<keyword>')
def restaurants_by_keyword(keyword):
    restaurants = query_db('SELECT * FROM restaurant WHERE description LIKE ?', ('%' + keyword + '%',))
    return render_template('restaurants.html', restaurants=restaurants, result_count=len(restaurants))

@app.route('/parse')
def parse():
    with open('resources/restaurants_opendata.csv', 'rb') as rest_csv:
        restaurant_list = []
        restaurants = csv.reader(rest_csv, delimiter = ';', encoding = 'utf-8')
        for row in restaurants:
            address = row[1].split(', ')
            zip_city = address[1].split(' ')
            row = row + [address[0]]
            row = row + [zip_city[0]]
            row = row + [zip_city[1]]
            insert_restaurant(row)
    return

@app.route('/categories/')
def categories():
    restaurants_asia = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ?',
        ('%asia%','%asien%', '%vietn%', '%korea%', '%fernost%', '%fernöstlich%'.decode('utf8'), '%indisch%', '%thai%', '%japan%', '%china%', '%chinesisch%'))

    restaurants_italy = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ?',
        ('%pizza%', '%italien%'))

    restaurants_cafe = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ? OR description LIKE ?',
        ('%café%'.decode('utf8'), '%cafe%', '%frühstück%'.decode('utf-8')))

    restaurants_spain = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ? OR description LIKE ?',
        ('%spanien%', '%spanisch%', '%tapas%'))

    restaurants_fish = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ?',
        ('%fisch%', '%meeres%'))

    restaurants_france = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ?',
        ('%frankreich%', '%französisch%'.decode('utf-8')))

    return render_template(
        'categories.html',
        restaurants_asia=restaurants_asia[:5],
        result_count_asia=len(restaurants_asia),
        restaurants_italy=restaurants_italy[:5],
        result_count_italy=len(restaurants_italy),
        restaurants_cafe=restaurants_cafe[:5],
        result_count_cafe=len(restaurants_cafe),
        restaurants_spain=restaurants_spain[:5],
        result_count_spain=len(restaurants_spain),
        restaurants_fish=restaurants_fish[:5],
        result_count_fish=len(restaurants_fish),
        restaurants_france=restaurants_france[:5],
        result_count_france=len(restaurants_france)
        )

@app.route('/categories/<category>')
def categories_detail(category):
    if category == 'asia':
        restaurants = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ?',
        ('%asia%','%asien%', '%vietn%', '%korea%', '%fernost%', '%fernöstlich%'.decode('utf8'), '%indisch%', '%thai%', '%japan%', '%china%', '%chinesisch%'))
    elif category == 'italy':
        restaurants = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ?',
        ('%pizza%', '%italien%'))
    elif category == 'cafe':
        restaurants = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ? OR description LIKE ?',
        ('%café%'.decode('utf8'), '%cafe%', '%frühstück%'.decode('utf-8')))
    elif category == 'spain':
        restaurants = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ? OR description LIKE ?',
        ('%spanien%', '%spanisch%', '%tapas%'))
    elif category == 'fish':
        restaurants = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ?',
        ('%fisch%', '%meeres%'))
    elif category == 'france':
        restaurants = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ?',
        ('%frankreich%', '%französisch%'.decode('utf-8')))
    return render_template('restaurants.html', restaurants=restaurants, result_count=len(restaurants))

@app.route('/detail/<int:restaurant_id>')
def detail(restaurant_id):
    restaurant = query_db('SELECT * FROM restaurant WHERE id = ?', (restaurant_id,), True)
    return render_template('detail.html', restaurant=restaurant)


def insert_restaurant(restaurant):
    db = get_db()
    db.execute("INSERT INTO restaurant VALUES (NULL, ?, ?, ?, ?, ?, ?)", (restaurant[0], restaurant[2], restaurant[3], restaurant[4], restaurant[6], restaurant[5]))
    db.commit();
    return