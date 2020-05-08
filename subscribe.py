import requests
import time
import os
import pprint as pp
from peewee import SqliteDatabase
from User import User

CLIENT_SECRET = None
CLIENT_ID = None
TWITCH_NAMES = None
SUBSCRIPTION_TIME = 864000

db = SqliteDatabase('following.db')

def create_tables():
    with db:
        db.create_tables([User])   

def get_env_vars():
    global CLIENT_SECRET
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
    global CLIENT_ID
    CLIENT_ID = os.environ['CLIENT_ID']
    global TWITCH_NAMES
    TWITCH_NAMES = os.environ['TWITCH_NAMES'].split(',')
    global REDIRECT_URL
    REDIRECT_URL = os.environ['REDIRECT_URL']

def prepare():
    get_env_vars()
    create_tables()
    api_setup()
    for username in TWITCH_NAMES:
        info = get_user_info(username)
        update_or_create(*info)


def api_setup():
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    print(params)
    r = requests.post('https://id.twitch.tv/oauth2/token', params=params)

    pp.pprint(r.json())
    app_token = r.json()['access_token']
    print(app_token)
    header = { 'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {app_token}' }

    time.sleep(0.5)
    r = requests.get('https://api.twitch.tv/helix/webhooks/subscriptions', headers=header)


def new_sub(user_id):
    print(user_id)
    data = {
        'hub.callback': REDIRECT_URL,
        'hub.mode': 'subscribe',
        'hub.topic': f'https://api.twitch.tv/helix/streams?user_id={user_id}',
        'hub.lease_seconds': SUBSCRIPTION_TIME
    }
    r = requests.post(
        'https://api.twitch.tv/helix/webhooks/hub', 
        headers={ 'Client-ID': CLIENT_ID }, 
        data=data
    )
    print(r)
    if r.status_code != 202:
        print(f"failure with new subscription for user {user_id}")
        pp.pprint(r.json())

def update_or_create(display_name, user_id, profile_image):
    user = User.get_or_none(User.user_id == int(user_id))
    if user is None:
        print(display_name)
        user = User.create(
            display_name=display_name,
            user_id=user_id,
            profile_image=profile_image
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
        headers={ 'Client-ID': CLIENT_ID }, 
        params={ 'login': name }
    )
    pp.pprint(r.json())
    data = r.json()['data'][0]
    display_name = data['display_name']
    user_id = data['id']
    profile_image = data['profile_image_url']
    return display_name, user_id, profile_image
