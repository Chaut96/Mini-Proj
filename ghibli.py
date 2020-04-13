from flask import Flask, request, jsonify
from cassandra.cluster import Cluster
import json
import requests

# Connecting to Cassandra cluster
cluster = Cluster(contact_points=['172.17.0.2'], port=9042)
session = cluster.connect()

# Setting up app settings
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Home route
@app.route('/')
def hello():
	intro ='<h1>Welcome to my app!</h1><p>To access the Cassandra DB, visit: /people</p><p>To access external Studio Ghibli data, visit: /people/external</p><p>To access data on a single Ghibli universe person, visit: /people/external/[id]</p>'
	return intro

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
def add_people():
	session.execute("""INSERT INTO ghibli.characters(id,name,age,gender,hair_colour,eye_colour) VALUES({},'{}',{},'{}','{}','{}')""".format(int(request.json['id']),request.json['name'],int(request.json['age']),request.json['gender'],request.json['hair_colour'],request.json['eye_colour']))
	return jsonify({'message':'created: /people/{}'.format(request.json['id'])}), 201

# Update an existing entry in the characters database
@app.route('/people', methods=['PUT'])
def update_people():
	session.execute("""UPDATE ghibli.characters SET name='{}',age={},gender='{}',hair_colour='{}',eye_colour='{}' WHERE id={}""".format(request.json['name'],int(request.json['age']),request.json['gender'],request.json['hair_colour'],request.json['eye_colour'],int(request.json['id'])))
	return jsonify({'message':'updated: /people/{}'.format(request.json['id'])}), 200

# Delete an existing entry in the characters database
@app.route('/people', methods=['DELETE'])
def delete_people():
	session.execute("""DELETE FROM ghibli.characters WHERE id={}""".format(int(request.json['id'])))
	return jsonify({'message':'deleted: /people/{}'.format(request.json['id'])}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
