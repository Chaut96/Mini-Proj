# Cloud Computing Mini Project
This Flask app connects to a Cassandra Cloud DB to store information. It is based upon Studio Ghibli's 
People API. The name, age, gender, hair colour and eye colour is stored with a unique ID. * To access the 
Cassandra DB: visit /people * To access the Studio Ghibli external API: visit /people/external * To access 
data on a single Ghibli universe person: visit /people/external/[id]
### Preparation
Installing required software ```bash sudo apt update sudo apt install docker.io sudo apt install 
python3-pip sudo pip3 install Flask ``` Creating a work directory ```bash mkdir app cd app ```
### Flask app code
``` wget -O ghibli.py https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/ghibli.py wget -O 
requirements.txt https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/requirements.txt ```
### Start up Cassandra
``` sudo docker pull cassandra:latest sudo docker run --name ghibli-startup -p 9042:9042 -d 
cassandra:latest ```
### Retrieving database data
``` wget -O characters.csv https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/people.csv sudo 
docker cp characters.csv ghibli-startup:/home/characters.csv ```
### Configuring Cassandra
Connecting to the database: ` sudo docker exec -it ghibli-startup cqlsh` ```cqlsh CREATE KEYSPACE ghibli 
WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1}; CREATE TABLE ghibli.characters (id 
int PRIMARY KEY,name text,age int,gender text,hair_colour text,eye_colour text); COPY 
ghibli.characters(id,name,age,gender,hair_colour,eye_colour) FROM '/home/characters.csv' WITH DELIMITER=',' 
AND HEADER=True; ``` *Before packaging, check node IP address matches with the app's cluster contact point* 
```sudo docker inspect ghibli-startup | grep IP Address```
### Packaging App into a Docker Image And Running
``` wget -O Dockerfile https://raw.githubusercontent.com/Chaut96/Mini-Proj/master/Dockerfile sudo docker 
build . --tag=ghibli:v1 sudo docker run -p 80:80 ghibli:v1 ```
