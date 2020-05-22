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
import argparse
from Store import Store

app = Flask(__name__)
db = SqliteDatabase('following.db')

def main():
    parser = argparse.ArgumentParser(description='Notify a Slack channel when Twitch users go live')
    parser.add_argument('-d', '--dev', action='store_true', dest='dev_mode')
    args = parser.parse_args()
    if args.dev_mode:
        print('Starting in dev mode')
        print('Instead of reading from Environment Variables, a local config.ini will be used')
        Store.setup('config.ini')
    else:
        subscribe.check_env_vars()
        Store.setup()

    Store.refresh_access_token()

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
            curr_time = int(time.time())
            last_live = user.last_live
            user.last_live = curr_time
            user.save()
            print(f'{user.display_name.capitalize()} is live!')
            if last_live is None:
                send_to_slack(data, user)
            else:
                if (curr_time - last_live) < 30*60:
                    print(f'{user.display_name.capitalize()} went live recently, not sending message')
                else:
                    send_to_slack(data, user)
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

def send_to_slack(data, user):
    stream = make_stream(data)
    message = make_message(user, stream)
    r = req.post(
        Store.slack_webhook,
        headers={ 'Content-type': 'application/json' },
        data=json.dumps(message)
    )
    print(r)

def subscription_handler():
    subscribe.prepare()
    while True:
        print("resubscribing to all")
        for user in User.select():
            subscribe.new_sub(user.user_id)
        time.sleep(Store.subscription_time - 120)

def user_handler():
    while True:
        for user in User.select():
            info = subscribe.get_user_info(user.display_name.lower())
            subscribe.update_or_create(*info)
        update_home()
        time.sleep(5 * 60 * 60)
        
def update_home():
    while True:
        pass
        # update home with new user data


if __name__ == '__main__':
    main()
