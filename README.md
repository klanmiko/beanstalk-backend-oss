# Beanstalk Open Source Backend

REST API Backend for beanstalk app. Stores posts, user profiles, manages authentication and generates user feeds. This is an open source copy of the backend submitted to ECS165. 
This open source repository was created after all final project submissions had been turned in.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Make sure you have a postgreSQL instance set up and running. Here is a good resource for learning how to create a new database and user [https://medium.com/coding-blocks/creating-user-database-and-adding-access-on-postgresql-8bfcd2f4a91e]

### Installing
First set up a virtualenv and install requirements

```
$ virtualenv venv
$ source venv/bin/activate # (unix)
$ venv\Scripts\activate # (windows)
$ pip3 install -r requirements.txt
```
Next you need to setup config.py:
```{python
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user="user",pw="password",url="url",db="db")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_ECHO = False
```

Make sure to set the db url, name, username, and password

# Running
```
flask run --host=0.0.0.0
```



## Authors
Kaelan Mikowicz
Annie Lin
Hiroka Tamura
Terry Yang
