from flask import Flask, request, jsonify, abort, url_for, g
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from cassandra.cluster import Cluster
import os
import json
import requests

# Connecting to Cassandra cluster
cluster = Cluster(contact_points=['172.17.0.2'], port=9042)
session = cluster.connect()

# Setting up app settings
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# User Database
class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(32), index= True)
	password_hash = db.Column(db.String(128))

	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

# Create database by force if needed
#db.create_all()

# User Registration
@app.route('/users', methods = ['POST'])
def new_user():
	username = request.json.get('username')
	password = request.json.get('password')
	if username is None or password is None:
		abort(400, 'Username or password is missing!')
	if User.query.filter_by(username = username).first() is not None:
		abort(400, 'That username already exists!')
	user = User(username = username)
	user.hash_password(password)
	db.session.add(user)
	db.session.commit()
	return jsonify({'username':user.username}), 201, {'Location':url_for('get_user', id=user.id, _external=True)}

# List users
@app.route('/users/<int:id>')
def get_user(id):
	user = User.query.get(id)
	if not user:
		abort(400, 'Unknown user ID')
	return jsonify({'username':user.username})

# Validate user credentials
@auth.verify_password
def verify_password(username, password):
	user = User.query.filter_by(username = username).first()
	if not user or not user.verify_password(password):
		return False
	g.user = user # store user as object in lifetime of app running
	return True

# Home route
@app.route('/')
def hello():
	intro ='<h1>Welcome to my app!</h1><p>To access the Cassandra DB, visit: /people</p><p>To access data on a single character in the DB: visit /people/[id]</p><p>To access external Studio Ghibli data, visit: /people/external</p><p>To access data on a single Ghibli universe person, visit: /people/external/[id]</p>'
	return intro

# User Register info
@app.route('/users', methods=['GET'])
def info():
	info ='<p>Please use a POST request containing a username and password to register</p>'
	return info
# Request state of characters database
@app.route('/people', methods=['GET'])
def get_people():
	rows = session.execute("""SELECT * FROM ghibli.characters""")
	result = []
	for r in rows:
		result.append({"id":r.id,"name":r.name,"age":r.age,"gender":r.gender,"hair_colour":r.hair_colour,"eye_colour":r.eye_colour})
	return jsonify(result)

# Request state of specified item in characters database
@app.route('/people/<id>', methods=['GET'])
def get_people_id(id):
        character = session.execute("""SELECT * FROM ghibli.characters WHERE id={}""".format(int(id)))
        result = []
        for c in character:
                result.append({"id":c.id,"name":c.name,"age":c.age,"gender":c.gender,"hair_colour":c.hair_colour,"eye_colour":c.eye_colour})
        return jsonify(result)

# Request state of Studio Ghibli API All People Endpoint
@app.route('/people/external', methods=['GET'])
def get_people_external():
	people_url = 'https://ghibliapi.herokuapp.com/people'
	response = requests.get(people_url)
	if response.ok:
		people = response.json()
		return jsonify(people), 200
	else:
		print(response.reason)

# Request state of Studio Ghibli API People ID Endpoint
@app.route('/people/external/<id>', methods=['GET'])
def get__people_id_external(id):
	select_people_url = 'https://ghibliapi.herokuapp.com/people/'
	response = requests.get(select_people_url+id)
	if response.ok:
		select_people = response.json()
		return jsonify(select_people), 200
	else:
		print (response.reason)

# Create a new entry into the characters database
@app.route('/people', methods=['POST'])
@auth.login_required
def add_people():
	session.execute("""INSERT INTO ghibli.characters(id,name,age,gender,hair_colour,eye_colour) VALUES({},'{}',{},'{}','{}','{}')""".format(int(request.json['id']),request.json['name'],int(request.json['age']),request.json['gender'],request.json['hair_colour'],request.json['eye_colour']))
	return jsonify({'message':'created: /people/{}'.format(request.json['id'])}), 201

# Update an existing entry in the characters database
@app.route('/people', methods=['PUT'])
@auth.login_required
def update_people():
	session.execute("""UPDATE ghibli.characters SET name='{}',age={},gender='{}',hair_colour='{}',eye_colour='{}' WHERE id={}""".format(request.json['name'],int(request.json['age']),request.json['gender'],request.json['hair_colour'],request.json['eye_colour'],int(request.json['id'])))
	return jsonify({'message':'updated: /people/{}'.format(request.json['id'])}), 200

# Delete an existing entry in the characters database
@app.route('/people', methods=['DELETE'])
@auth.login_required
def delete_people():
	session.execute("""DELETE FROM ghibli.characters WHERE id={}""".format(int(request.json['id'])))
	return jsonify({'message':'deleted: /people/{}'.format(request.json['id'])}), 200

if __name__ == '__main__':
	if not os.path.exists('db.sqlite'):
		db.create_all()
	app.run(host='0.0.0.0', port=8080)
