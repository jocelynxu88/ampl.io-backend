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

@app.route('/getUsername/<FriendCode>', methods = ['GET'])
def getUsername(FriendCode):
    try:
        doc_ref = db.collection('users').where('FriendCode', '==', FriendCode).stream()
        doc_ref = list(doc_ref)

        print(doc_ref)
        
        return doc_ref[0].id, 200
    except Exception as e:
        print(e)
        return "bad", 400

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

@app.route('/userMessages', methods=['GET'])
def userMessages():
    username = request.args.get('username');
    group_ref = db.collection(u'UserMessages').document(username);
    results = group_ref.get();
    groupMessages = results.to_dict();

    messages = [];

    for i in groupMessages['Groups']:
        message = db.collection(u'GroupChats').document(i['ChatId']).get().to_dict();
        message['read'] = i['read'];
        message['name'] = i['name'];
        message['id'] = i['ChatId'];

        messages.append(message);

    return {'messages': messages };

@app.route('/sendMessage', methods=['POST'])
def sendMessage():
    requestForm = request.get_json();

    message_ref = db.collection(u'GroupChats').document(requestForm['ChatId']);
    message_ref.update({u'Messages': firestore.ArrayUnion([{'message': requestForm['message'], 'sender': requestForm['username'], 'id': requestForm['id']}])});
    
    users = message_ref.get().to_dict();
    users = users['members']; #now we need to go set all these to unread for the users

    for user in users:
        if user == requestForm['username']:
            continue;

        user_ref = db.collection(u'UserMessages').document(user)
        user_groups = user_ref.get().to_dict();
        user_groups = user_groups['Groups'];

        for i in range(len(user_groups)):
            if user_groups[i]['ChatId'] == requestForm['ChatId']:
                user_groups[i]['read'] = False;
                break;

        user_ref.update({u'Groups': user_groups});
    
    return {"message": "sent"}

@app.route('/getMessages', methods=['GET'])
def getMessages():
    messages = db.collection(u'GroupChats').document(request.args.get('ChatId')).get().to_dict();
    user_ref = db.collection(u'UserMessages').document(request.args.get('username'));

    user_groups = user_ref.get().to_dict();
    user_groups = user_groups['Groups'];

    for i in range(len(user_groups)):
        if user_groups[i]['ChatId'] == request.args.get('ChatId'):
            user_groups[i]['read'] = True;
            break;

    user_ref.update({u'Groups': user_groups});

    return {"messages": messages['Messages']}
