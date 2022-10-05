from collections import UserList
from marshal import dumps
import os
import json
import re
from unicodedata import name
from flask import Flask, request, Response, jsonify
from bson.objectid import ObjectId
import pymongo
from flask_cors import CORS



# MongoDB connection string
MONGO_URI = os.getenv('MONGO_URI')

# Create Flask app
app = Flask(__name__)
CORS(app)
# Create connection to MongoDB
try:
    client = pymongo.MongoClient(MONGO_URI)
    print('Connected to MongoDB')
    db = client.users
    print(db)

except Exception as ex:
    print('Error - Cannot connect to db!', str(ex))


@app.route('/')
def welcome():
    return 'Welcome to the Flask App with MongoDB'

# Create a new user in the database and return the user id as a response


@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        user = request.json
        db.users.insert_one(user)
        return Response(status=201, mimetype='application/json', response=json.dumps({'id': str(user['_id']), 'message': 'User created successfully'}))

    except Exception as ex:
        print('Error - Cannot create user!', str(ex))

# Get a single user from the database and return it as a JSON object
@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        print(id)
        user = db.users.find_one({'id': id})
        user['id'] = user['id']
        user['_id'] = str(user['_id'])

        return Response(status=200, mimetype='application/json', response=json.dumps(user))
    except Exception as ex:
        print('Error - Cannot get user!', str(ex))

# Update a single user in the database and return the user id as a response


@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        print(id)
        user = request.json
        print(user)
        user['id'] = user['id']
        user['_id'] = str(user['_id'])
        db.users.update_one({'_id': id}, {'$set': user})

        return Response(status=200, mimetype='application/json', response=json.dumps(user))
    except Exception as ex:
        print('Error - Cannot update user!', str(ex))

# Delete a single user from the database and return the user id as a response


@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = request.json
        print(user)
        user['id'] = user['id']
        user['_id'] = str(user['_id'])
        user= db.users.delete_one({'id': id})
    
        return Response(status=200, mimetype='application/json', response=json.dumps({'id': str(id), 'message': 'User deleted'}))
    except Exception as ex:
        print('Error - Cannot delete user!', str(ex))


# search for a user by name
@app.route('/api/users/search', methods=['GET'])
def search_user():
    try:

        first_name = request.args.get('first_name')
        user = db.users.find_one({'first_name': first_name})
        users = list(db.users.find({'first_name': first_name}))
        for user in users:
            user['_id'] = str(user['_id'])
        return Response(status=200, mimetype='application/json', response=json.dumps({'users': users, 'count': len(users)}))
    except Exception as ex:
        print('Error - Cannot get users!', str(ex))


@app.route('/api/users', methods=['GET'])
def get_userss():
    try:
        user = db.users
        #if page and limit are not specified, return all users
        if not request.args.get('page') and not request.args.get('limit') and not request.args.get('name'):
            users = list(user.find())
            for user in users:
                user['_id'] = str(user['_id'])
            return Response(status=200, mimetype='application/json', response=json.dumps({'users': users}))
        #if page and limit are specified, return users based on page and limit not name specified
        if request.args.get('page') and request.args.get('limit') and not request.args.get('name'):
            page = int(request.args.get('page'))
            limit = int(request.args.get('limit'))
            users = list(user.find().skip((page-1)*limit).limit(limit))
            for user in users:
                user['_id'] = str(user['_id'])
            return Response(status=200, mimetype='application/json', response=json.dumps({'users': users}))
         #if page and limit not specified, return users based on name
        if request.args.get('name') and not request.args.get('page') and not request.args.get('limit'): 
            name = request.args.get('name')
            users = list(user.find({'$or': [{'first_name': re.compile(name, re.IGNORECASE)}, {'last_name': re.compile(name, re.IGNORECASE)}]}))
            for user in users:
                user['_id'] = str(user['_id'])
            return Response(status=200, mimetype='application/json', response=json.dumps({'users': users}))   
        elif request.args.get('page') and request.args.get('limit'):
            page = int(request.args.get('page'))
            limit = int(request.args.get('limit'))
            skip = (page - 1) * limit
            name = request.args.get('name')
        #first_name and last_name are comibined to search for a user by name with substring matching
        #sort by age in ascending order by default and descending order if specified
            if request.args.get('sort') == '-age':
                users = list(user.find({'$or': [{'first_name': re.compile(name, re.IGNORECASE)}, {'last_name': re.compile(name, re.IGNORECASE)}]}).sort('age', pymongo.DESCENDING).skip(skip).limit(limit))
            else:
                users = list(user.find({'$or': [{'first_name': re.compile(name, re.IGNORECASE)}, {'last_name': re.compile(name, re.IGNORECASE)}]}).sort('age', pymongo.ASCENDING).skip(skip).limit(limit))
        for user in users:
                user['_id'] = str(user['_id'])      
        return Response(status=200, mimetype='application/json', response=json.dumps({'users': users}))

    except Exception as ex:
        print('Error - Cannot get users!', str(ex))       


if __name__ == '__main__':
    app.run(debug=True,port=int(os.environ.get("PORT", 5000)))
