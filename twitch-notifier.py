import os
import json
import requests as req
import pprint as pp
import time
from flask import Flask, request, jsonify
from peewee import SqliteDatabase
from User import User
from helpers import *
import threading
import subscribe

ENV_VAR_STRINGS = [
    'TWITCH_NAMES',
    'CLIENT_ID',
    'CLIENT_SECRET',
    'REDIRECT_URL',
    'SLACK_WEBHOOK'
]

SLACK_WEBHOOK = None
SUBSCRIPTION_TIME = 864000
SLACK_HEADER = {
    'Content-type': 'application/json',
}

app = Flask(__name__)
db = SqliteDatabase('following.db')

def main():
    missing_env_var = False
    for env_var in ENV_VAR_STRINGS:
        if env_var not in os.environ:
            print(f"Environment variable '{env_var}' not found!")
            missing_env_var = True
    if missing_env_var:
        print("Exiting!")
        exit()

    global SLACK_WEBHOOK
    SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']

    subscribe_refresh = threading.Thread(target=subscription_handler, daemon=True)
    subscribe_refresh.start()
    app.run(host='0.0.0.0', port=5000)


@app.route('/twitchbot', methods=['POST'])
def user_update():
    data = request.get_json()['data']
    if data:
        data = data[0]
        if data['type'] == 'live':
            user_id = data['user_id']
            user = User.get(User.user_id == int(user_id))
            user.last_live = int(time.time())
            user.save()
            print(f'{user.display_name.capitalize} is live!')
            stream = make_stream(data)
            message = make_message(user, stream)
            message_json = json.dumps(message)
            r = req.post(SLACK_WEBHOOK, headers=SLACK_HEADER, data=message_json)
            print(r)
    else:
        print('Empty Data - Stream ended')
    return jsonify(success=True)

@app.route('/twitchbot', methods=['GET'])
def accept_challenge():
    print('got GET')
    challenge = request.args.get('hub.challenge')
    topic = request.args.get('hub.topic')
    user_id = topic.split('user_id=')[-1]
    # print(challenge)
    # print(user_id)
    user = User.get(User.user_id == int(user_id))
    user.last_subscribed = int(time.time())
    user.save()
    return challenge, 200, {'ContentType':'text/plain'}

@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    db.close()
    return response

def subscription_handler():
    subscribe.prepare()
    while(True):
        print("resubscribing to all")
        for user in User.select():
            subscribe.new_sub(user.user_id)
        time.sleep(SUBSCRIPTION_TIME - 120)

if __name__ == '__main__':
    main()
