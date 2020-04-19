# Cloud Computing Mini Project
This Flask app connects to a Cassandra Cloud DB to store fictional characters.  
It is based upon Studio Ghibli's People API: https://ghibliapi.herokuapp.com/  
The name, age, gender, hair colour and eye colour is stored with a unique ID.

* Resources
  * To manage DB users: visit /users
  * To access the Cassandra DB: visit /people
  * To access data on a single character in the DB: visit /people/[id]
  * To access the Studio Ghibli external people API: visit /people/external
  * To access data on a single Ghibli universe person: visit /people/external/[id]

## Setup
### Preparing app environment
Creating a work directory:
```bash
mkdir characters-app
cd characters-app
```

Downloading app files (or clone):
```bash
wget -O requirements.txt https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/requirements.txt
wget -O ghibli.py https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/ghibli.py
wget -O characters.csv https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/characters.csv
```

Installing requirements and retrieving app code:
```bash
sudo apt update
sudo apt install docker.io
sudo apt install python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install -r requirements.txt
```

### Preparing Cassandra
Pulling the latest cassandra image from Docker.io and running under a chosen name with port binding to 9042 in detached mode:
```bash
sudo docker pull cassandra:latest
sudo docker run --name ghibli-startup -p 9042:9042 -d cassandra:latest
```

Copying data into the image's `/home/` directory:
```bash
sudo docker cp characters.csv ghibli-startup:/home/characters.csv
```

### Configuring Cassandra
Connecting to the database:
```bash
sudo docker exec -it ghibli-startup cqlsh
```

Setting up the keyspace, table and populating it:
```cqlsh
CREATE KEYSPACE ghibli WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};
CREATE TABLE ghibli.characters (id int PRIMARY KEY,name text,age int,gender text,hair_colour text,eye_colour text);
COPY ghibli.characters(id,name,age,gender,hair_colour,eye_colour) FROM '/home/characters.csv' WITH DELIMITER=',' AND HEADER=True;
```

Viewing the database:
```cqlsh
SELECT * FROM  ghibli.characters;
EXIT
```

Checking node IP address matches with the app's cluster contact point:
```bash
sudo docker inspect ghibli-startup | grep IPAddress
nano ghibli.py
```
### Running the App (Option #1)
To run the app directly:
```bash
python3 ghibli.py
```

### Packaging App into a Docker Image And Running (Option #2)
Retrieving dockerfile instructions and building the docker image for the app to run:
```bash
wget -O Dockerfile https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/Dockerfile
sudo docker build . --tag=ghibli:v1
sudo docker run -p 8080:8080 ghibli:v1
```

## API Documentation

* **POST** /users

Registers a new user stored in an SQLAlchemy DB.  
The request must be a JSON object containing a `username` and `password` field.  
The password is hashed before storing in the database, and the original password is not saved.  
Returns status code 201. Example:
```bash
curl -i -H "Content-Type:application/json" -X POST -d '{"username":"tommy","password":"drapers"}' http://ec2-3-83-151-231.compute-1.amazonaws.com:8080/users
```

* **GET** /people

Returns all characters from the characters table.  
Returns status code 200. Example:
```bash
curl -i http://ec2-3-83-151-231.compute-1.amazonaws.com:8080/people
```

* **GET** /people/[id]

Returns a single character from the characters table.  
Returns status code 200. Example:
```bash
curl -i http://ec2-3-83-151-231.compute-1.amazonaws.com:8080/people/1
```

* **GET** /people/external

Returns all the characters from the Studio Ghibli People API.  
Returns status code 200. Example:
```bash
curl -i http://ec2-3-83-151-231.compute-1.amazonaws.com:8080/people/external
```

* **GET** /people/external/[id]

Returns a single character from the Studio Ghibli People API.  
Returns status code 200. Example:
```bash
curl -i http://ec2-3-83-151-231.compute-1.amazonaws.com:8080/people/external/ca568e87-4ce2-4afa-a6c5-51f4ae80a60b
```
* **POST** /people

Requires server authenication.  
Creates a new entry in the characters table.  
Returns a status code 201. Example:
```bash
curl -i -u tommy:drapers -H "Content-Type: application/json" -X POST -d '{"id":5,"age":0,"name":"Bobby","gender":"Male","hair_colour":"NA","eye_colour":"Blue"}' http://ec2-3-83-151-231.compute-1.amazonaws.com:8080/people
```

* **PUT** /people

Requires server authenication.  
Modifies an existing entry in the characters table.  
Returns a status code 200. Example:
```bash
curl -i -u tommy:drapers -H "Content-Type: application/json" -X PUT -d '{"id":5,"age":5,"name":"Bobby","gender":"Male","hair_colour":"Blue","eye_colour":"Blue"}' http://ec2-3-83-151-231.compute-1.amazonaws.com:8080/people
```

* **DELETE** /people

Requires server authenication.  
Deletes an existing entry in the characters table.  
Returns a status code 200. Example:
```bash
curl -i -u tommy:drapers -H "Content-Type: application/json" -X DELETE -d '{"id":5}' http://ec2-3-83-151-231.compute-1.amazonaws.com:8080/people
```
```
