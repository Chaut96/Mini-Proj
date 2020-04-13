# Cloud Computing Mini Project
This Flask app connects to a Cassandra Cloud DB to store information.
It is based upon Studio Ghibli's People API: https://ghibliapi.herokuapp.com/

The name, age, gender, hair colour and eye colour is stored with a unique ID.

* To access the Cassandra DB: visit /people
* To access the Studio Ghibli external API: visit /people/external
* To access data on a single Ghibli universe person: visit /people/external/[id]

## Setup
### Preparation
Installing required software
```bash
sudo apt update
sudo apt install docker.io
sudo apt install python3-pip
sudo pip3 install Flask
```
Creating a work directory
```bash
mkdir app
cd app
```

### Retrieving Flask App Code Files
Retrieving files needed from the repository
```bash
wget -O ghibli.py https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/ghibli.py
wget -O requirements.txt https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/requirements.txt
```

### Running Cassandra DB
Pulling the latest cassandra image from Docker.io and running under a chosen name with port binding to 9042 in detached mode
```bash
sudo docker pull cassandra:latest
sudo docker run --name ghibli-startup -p 9042:9042 -d cassandra:latest
```

### Retrieving Database Data
Retrieving csv file from the repository and copying into the image's `/home/` directory
```bash
wget -O characters.csv https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/characters.csv
sudo docker cp characters.csv ghibli-startup:/home/characters.csv
```

### Configuring Cassandra
Connecting to the database: `sudo docker exec -it ghibli-startup cqlsh`

Setting up the keyspace, table and populating it
```cqlsh
CREATE KEYSPACE ghibli WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};
CREATE TABLE ghibli.characters (id int PRIMARY KEY,name text,age int,gender text,hair_colour text,eye_colour text);
COPY ghibli.characters(id,name,age,gender,hair_colour,eye_colour) FROM '/home/characters.csv' WITH DELIMITER=',' AND HEADER=True;
```
Checking the database has the correct data:
`SELECT * FROM  ghibli.characters;`
The table should appear similar to:

| id | age | eye_colour | gender | hair_colour | name|
|---:|---:|---:|---:|---:|---:|
|1|18|Brown|Female|Blue|Maria|
|2|40|Brown|Male|Black|Ferghus|
|4|30|Red|Female|Red|Lassar|
|3|20|Blue|Male|Blonde|Deian|

`EXIT;` and continue if data is correct

*Before packaging, check node IP address matches with the app's cluster contact point*
```bash
sudo docker inspect ghibli-startup | grep IPAddress
nano ghibli.py
```

### Packaging App into a Docker Image And Running
Retrieving dockerfile instructions and building the docker image for the app to run
```bash
wget -O Dockerfile https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/Dockerfile
sudo docker build . --tag=ghibli:v1
sudo docker run -p 80:80 ghibli:v1
```
## Running The App
The app will run on the machine's localhost.
Example cURLs:
```bash
curl -i http://0.0.0.0/people
curl -i -H "Content-Type: application/json" -X POST -d  '{"id":5,"age":0,"name":"Bobby","gender":"Male","hair_colour":"NA","eye_colour":"Blue"}' http://0.0.0.0/people
curl -i -H "Content-Type: application/json" -X PUT -d '{"id":5,"age":5,"name":"Bobby","gender":"Male","hair_colour":"Blue","eye_colour":"Blue"}' http://0.0.0.0/people
curl -i -H "Content-Type: application/json" -X DELETE -d '{"id":5}' http://0.0.0.0/people
```
