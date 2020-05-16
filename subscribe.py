import requests
import time
import os
import pprint as pp
from peewee import SqliteDatabase
from User import User
from Store import Store


ENV_VAR_STRINGS = [
    'TWITCH_NAMES',
    'CLIENT_ID',
    'CLIENT_SECRET',
    'REDIRECT_URL',
    'SLACK_WEBHOOK'
]

db = SqliteDatabase('following.db')

def check_env_vars():
    missing_env_var = False
    for env_var in ENV_VAR_STRINGS:
        if env_var not in os.environ:
            print(f"Environment variable '{env_var}' not found!")
            missing_env_var = True
    if missing_env_var:
        print("Exiting!")
        exit()

def create_tables():
    with db:
        db.create_tables([User])   

def prepare():
    create_tables()
    for username in Store.twitch_names:
        info = get_user_info(username)
        update_or_create(*info)

def new_sub(user_id):
    print(user_id)
    data = {
        'hub.callback': Store.redirect_url,
        'hub.mode': 'subscribe',
        'hub.topic': f'https://api.twitch.tv/helix/streams?user_id={user_id}',
        'hub.lease_seconds': Store.subscription_time
    }
    r = requests.post(
        'https://api.twitch.tv/helix/webhooks/hub', 
        headers=Store.default_header, 
        data=data
    )
    print(r)
    if r.status_code != 202:
        print(f"failure with new subscription for user {user_id}")
        pp.pprint(r.json())

def update_or_create(display_name, user_id, profile_image,broadcaster_type):
    user = User.get_or_none(User.user_id == int(user_id))
    if user is None:
        print(display_name)
        user = User.create(
            display_name=display_name,
            user_id=user_id,
            profile_image=profile_image,
            broadcaster_type=broadcaster_type
        )
    else:
        print(display_name)
        print(user.display_name)
        user.display_name = display_name
        user.profile_image = profile_image
    user.save()
    print(user.display_name)

def get_user_info(name):
    r = requests.get(
        'https://api.twitch.tv/helix/users', 
        headers=Store.default_header, 
        params={ 'login': name }
    )
    pp.pprint(r.json())
    data = r.json()['data'][0]
    display_name = data['display_name']
    user_id = data['id']
    profile_image = data['profile_image_url']
    broadcaster_type = data['broadcaster_type']
    return display_name, user_id, profile_image, broadcaster_type
