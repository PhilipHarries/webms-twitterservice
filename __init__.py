from flask import Flask, jsonify, abort, make_response, request, url_for
from flask.ext.pymongo import PyMongo
import datetime
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

handler = RotatingFileHandler('./logs/twitterservice.log',maxBytes=40960,backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addHandler(handler)


# connect to mongo with defaults
mongo = PyMongo(app)

debug = True
def dpr(s):
    app.logger.error(s)
    if(debug):
        print s


def make_public_tweet(tweet):
    new_tweet = {}
    for field in tweet:
        if field == 'id':
            new_tweet['uri'] = url_for(
                                    'get_tweet',
                                    tweet_id=tweet['id'],
                                    _external = True
                                    )
        if field == '_id':
            pass
        else:
            try:
                new_tweet[field] = tweet[field]
            except Exception as e:
                dpr("{} - {}".format(field, e))
    return new_tweet


def make_public_user(user):
    new_user = {}
    for field in user:
        if field == 'id':
            new_user['uri'] = url_for(
                                    'get_user',
                                    user_id=user['id'],
                                    _external = True
                                    )
        if field == '_id':
            pass
        else:
            try:
                new_user[field] = user[field]
            except Exception as e:
                dpr("{} - {}".format(field, e))
    return new_user


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': '404: not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': '400: bad request'}), 400)

@app.errorhandler(409)
def bad_request(error):
    return make_response(jsonify({'error': '409: duplicate resource id'}), 409)

@app.route('/twitter/api/v1.0/users', methods=['GET'])
def get_users():
    users=[]
    cursor=mongo.db.users.find()
    for user in cursor:
        users.append(user)
    if len(users) !=0:
        return jsonify({'users': [make_public_user(user) for user in users]})
    else:
        abort(404)

@app.route('/twitter/api/v1.0/user/<string:user_id>', methods=['GET'])
def get_user(user_id):
    cursor=mongo.db.users.find()
    user = [user for user in cursor if user['id'] == user_id]
    if len(user) == 0:
        abort(404)
    return jsonify({'user': make_public_user(user[0])})

@app.route('/twitter/api/v1.0/user/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user=mongo.db.users.find_one_or_404({'id': user_id})
    if len(user) == 0:
        abort(404)
    mongo.db.users.remove({"id": user_id})
    mongo.db.tweets.remove({"owning_id": user_id})
    return jsonify({'result': True})


@app.route('/twitter/api/v1.0/users', methods=['POST'])
def create_user():
    if not request.json or not 'id' in request.json:
        abort(400)
    user = {
        'id': request.json['id'],
        }
    cursor=mongo.db.users.find({'id': user['id']}).limit(1)
    if cursor.count() > 0:
        abort(409)
    mongo.db.users.insert(user)
    return jsonify({'user': make_public_user(user)}), 201

@app.route('/twitter/api/v1.0/tweets/<string:user_id>', methods=['GET'])
def get_tweets(user_id):
    tweets=[]
    cursor=mongo.db.tweets.find()
    tweets = [tweet for tweet in cursor if tweet["owning_id"] == user_id]
    if len(tweets) != 0:
        return jsonify({'tweets': [make_public_tweet(tweet) for tweet in tweets]})
    else:
        abort(404)

@app.route('/twitter/api/v1.0/tweet/<string:tweet_id>', methods=['GET'])
def get_tweet(tweet_id):
    cursor=mongo.db.tweets.find()
    tweet = [tweet for tweet in cursor if tweet["id"] == int(tweet_id)]
    if len(tweet) == 0:
        abort(404)
    return jsonify({'tweet': make_public_tweet(tweet[0])})

if __name__ == '__main__':
    app.run(debug=True,port=6544)


