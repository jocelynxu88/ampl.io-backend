from flask import Flask, jsonify
from flask import request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random 

cred = credentials.Certificate("ruhacks-9ee0f-firebase-adminsdk-86qne-55ae789d4f.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)

@app.route('/')
def hello_world():
    # Add a new document
    doc_ref = db.collection(u'users').document(u'alovelace')
    doc_ref.set({
        u'first': u'Ada',
        u'last': u'Lovelace',
        u'born': 1815
    })

    # Then query for documents
    users_ref = db.collection(u'users')

    for doc in users_ref.stream():
        print(u'{} => {}'.format(doc.id, doc.to_dict()))
    return 'Hello, Worldd!'

@app.route('/getGoals/<username>', methods = ['GET'])
def getGoals(username):
    try:
        doc_ref = db.collection('users').document(username).collection('Goals').stream()

        arr = [doc.to_dict() for doc in doc_ref]

        return jsonify(arr), 200
    except Exception as e:
        print("yikes: ", e)
        return 'bad', 400

def match(username):
    try: 
        currFriendCode = db.collection('users').document(username).get().to_dict()['FriendCode']
        
        doc_ref = db.collection('userIds').where('FriendCode', '!=', currFriendCode).stream()
        
        userIds = [doc.to_dict()['FriendCode'] for doc in doc_ref]

        userIds = random.sample(userIds, 3)

        doc_ref = list(db.collection('users').where('FriendCode', 'in', userIds).stream())
        
        usernames = [doc.id for doc in doc_ref]

        usernames += [username]

        print(usernames)
        
        return usernames
    except Exception as e:
        print("uh oh", e)
        return []


@app.route('/createGoal/<username>', methods = ['POST'])
def goals(username):
    try:
        doc_ref = db.collection('users').document(username).collection('Goals')

        friends = []
        if 'friends' in request.json.keys():
            friends = request.json['friends']
        else:
            friends = match(username)

        doc_ref.add({'name' : request.json['name'], 'frequency' : request.json['frequency'], 
        'category' : request.json['category'], 'complete' : [], 'incomplete' : friends})
        print("USERNAME: " + username)
        print(request.json)
        return "good", 200
    except Exception as e:
        print(e)
        return 'bad', 400