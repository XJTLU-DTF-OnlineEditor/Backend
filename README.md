# Backend
This is a breif guide to set up the environment and run the backend
## Local deployment
1. pip install -r requirements-txt
2. docker run -p 6379:6379 -d redis:5
3. docker pull blue776/py:1
2. python manage.py runserver 0.0.0.0:8001
## server deployment
### Normal deployment
1. Creat vertual environment and enter the virtualenv
2. pip install -r requirements-txt
3. docker run -p 6379:6379 -d redis:5
4. docker pull blue776/py:1
5. nohup python manage.py runserver 0.0.0.0:8001
### using docker
1. docker build . -t backend-dev
2. docker pull blue776/py:1
3. docker run -p 6379:6379 -d redis:5
2. docker run -d -p 8000:8001 -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker backend-dev



# 1. run 
## data flow:
browser -> (post req) -> django page -> (stores file in /tmp/code.py) -> 
docker run -> (execute code) -> (store result in /tmp/code.out) -> 
(response to browser) -> browser callback (update UI)

## docker image && container
We can use: `docker pull python:3.5.2-alpine` as our running image,
and then, use volume to mount `tmp/code.py` on the host with `/tmp/code.py`
in the container. Then, execute, output content to file on host, you can reference:
https://github.com/besnik/simple-python-online-editor/blob/master/run_in_docker.sh

## create Django cache

type 'python manage.py createcachetable cache_table_home' by terminal under the project root
use "pip install -r requirements.txt" to install needed pip under the root file
before using the courseApp you need "python manage.py makemigrations" & "python manage.py migrate" to rebuild the database 

