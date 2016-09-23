#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
import sqlite3
import unicodecsv as csv
from flask import Flask, render_template, g, flash, request, session, redirect, url_for

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
@app.route('/user/<int:user_id>')
def user(user_id): # Informationen über einen Benutzer
	user = query_db('SELECT *, COUNT(rating.id) as ratings FROM user LEFT JOIN rating ON rating.user_id = user.id WHERE user.id = ? GROUP BY user.id', (user_id,), True)
	return render_template('user.html', user = user, session_user=get_user(session.get('user_id')))
	
@app.route('/')
@app.route('/restaurants')
def restaurants(): # Liste aller Restaurants anzeigen
	restaurants = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id GROUP BY restaurant.id ORDER BY avg_rating DESC')
	return render_template('restaurants.html', restaurants=restaurants, result_count=len(restaurants), session_user=get_user(session.get('user_id')))

@app.route('/restaurants/keyword/<keyword>')
def restaurants_by_keyword(keyword): # Restaurants anzeigen, die ein bestimmtes Stichwort in der Beschreibung enthalten
	restaurants = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR name LIKE ? OR city LIKE ? OR zip LIKE ? OR street LIKE ? GROUP BY restaurant.id', ('%' + keyword + '%','%' + keyword + '%','%' + keyword + '%','%' + keyword + '%','%' + keyword + '%',))
	return render_template('restaurants.html', restaurants=restaurants, result_count=len(restaurants), session_user=get_user(session.get('user_id')))

@app.route('/search_form')
def search_form(): # Suchformular anzeigen
	return render_template('search.html', session_user=get_user(session.get('user_id')))

@app.route('/parse')
def parse(): # Datei parsen, wird nur einmal benötigt
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
def categories(): # Kategorien anzeigen
	restaurants_asia = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY rating DESC',
		('%asia%','%asien%', '%vietn%', '%korea%', '%fernost%', '%fernöstlich%'.decode('utf8'), '%indisch%', '%thai%', '%japan%', '%china%', '%chinesisch%'))

	restaurants_italy = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY rating DESC',
		('%pizza%', '%italien%'))

	restaurants_cafe = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY rating DESC',
		('%café%'.decode('utf8'), '%cafe%', '%frühstück%'.decode('utf-8')))

	restaurants_spain = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY rating DESC',
		('%spanien%', '%spanisch%', '%tapas%'))

	restaurants_fish = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY rating DESC',
		('%fisch%', '%meeres%'))

	restaurants_france = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY rating DESC',
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
		result_count_france=len(restaurants_france),
		session_user=get_user(session.get('user_id'))
		)

@app.route('/categories/<category>')
def categories_detail(category): # Eine Kategorie anzeigen
	if category == 'asia':
		restaurants = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY avg_rating DESC',
		('%asia%','%asien%', '%vietn%', '%korea%', '%fernost%', '%fernöstlich%'.decode('utf8'), '%indisch%', '%thai%', '%japan%', '%china%', '%chinesisch%'))
	elif category == 'italy':
		restaurants = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY avg_rating DESC',
		('%pizza%', '%italien%'))
	elif category == 'cafe':
		restaurants = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY avg_rating DESC',
		('%café%'.decode('utf8'), '%cafe%', '%frühstück%'.decode('utf-8')))
	elif category == 'spain':
		restaurants = query_db('SELECT * FROM restaurant WHERE description LIKE ? OR description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY avg_rating DESC',
		('%spanien%', '%spanisch%', '%tapas%'))
	elif category == 'fish':
		restaurants = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY avg_rating DESC',
		('%fisch%', '%meeres%'))
	elif category == 'france':
		restaurants = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON rating.restaurant_id = restaurant.id WHERE description LIKE ? OR description LIKE ? GROUP BY restaurant.id ORDER BY avg_rating DESC',
		('%frankreich%', '%französisch%'.decode('utf-8')))
	return render_template('restaurants.html', restaurants=restaurants, result_count=len(restaurants), session_user=get_user(session.get('user_id')))

@app.route('/detail/<int:restaurant_id>')
def detail(restaurant_id): # Details zu einem Restaurant anzeigen
	restaurant = query_db('SELECT *, COALESCE(ROUND(AVG(rating), 1), 0.0) as avg_rating FROM restaurant LEFT JOIN rating ON restaurant.id = rating.restaurant_id WHERE restaurant.id = ?', (restaurant_id,), True)
	ratings = query_db('SELECT * FROM rating JOIN user ON rating.user_id = user.id WHERE restaurant_id = ?', (restaurant_id,))
	return render_template('detail.html', restaurant=restaurant, ratings=ratings, session_user=get_user(session.get('user_id')))

@app.route('/login_form')
def login_form(): # Login-Formular
	return render_template('login_form.html', session_user=get_user(session.get('user_id')))

@app.route('/login', methods=['GET'])
def login(): # Login
	user = query_db('SELECT * FROM user WHERE name = ? AND password = ?', (request.args.get('name',''), request.args.get('password','')), True)
	if user == None:
		return render_template('login_form.html', session_user=get_user(session.get('user_id')))
	else:
		session['user_id'] = user['id']
		return render_template('user.html', user = user, session_user=get_user(session.get('user_id')))

@app.route('/logout')
def logout(): # Ausloggen
	session['user_id'] = 0
	return render_template('login_form.html', session_user=get_user(session.get('user_id')))

@app.route('/register_form')
def register_form(): # Registrierungs-Formular
	return render_template('register_form.html', session_user=get_user(session.get('user_id')))

@app.route('/register', methods=['GET'])
def register(): # Registrierung

	name = request.args.get('name','')
	email = request.args.get('email','')
	password = request.args.get('password', '')
	password_repeat = request.args.get('password_repeat', '')

	if password == password_repeat:
		db = get_db()
		db.execute('INSERT INTO user VALUES (null, ?, ?, ?)', (name, email, password))
		db.commit()

	user = query_db('SELECT * FROM user WHERE name = ? AND email = ?', (name, email), True)
	
	if user == None:
		return render_template('register_form.html', session_user=get_user(session.get('user_id')))
	else:
		return render_template('user.html', user = user, session_user=get_user(session.get('user_id')))

@app.route('/rate', methods=['GET'])
def rate(): # Bewertung für ein Restaurant abgeben
	restaurant_id = request.args.get('restaurant_id', '')
	user_id = request.args.get('user_id','')
	rating = request.args.get('rating','')
	text = request.args.get('text','')

	db = get_db()
	db.execute("INSERT INTO rating VALUES (NULL, ?, ?, ?, ?)", (restaurant_id, user_id, rating, text))
	db.commit()
	
	return redirect(url_for(".detail", restaurant_id=restaurant_id))


def insert_restaurant(restaurant): # Im Import-Prozess verwendet
	db = get_db()
	db.execute("INSERT INTO restaurant VALUES (NULL, ?, ?, ?, ?, ?, ?)", (restaurant[0], restaurant[2], restaurant[3], restaurant[4], restaurant[6], restaurant[5]))
	db.commit()
	return

def get_user(user_id): # Einen User anhand seiner ID aus der Datenbank holen
	if user_id != None:
		user = query_db('SELECT * FROM user WHERE id = ?', (user_id,), True)
	else:
		user = None
	return user