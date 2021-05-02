from flask import Flask
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

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

@app.route('/users')
def users():
    return 'Hello'

@app.route('/goals')
def goals():
    return {'a' : 1, 'b': 2}