import requests
import os
import configparser
import pprint as pp

class Store(object):
    access_token = None
    slack_webhook = None
    client_id = None
    client_secret = None
    redirect_url = None
    twitch_names = []
    subscription_time = 864000
    default_header = {}

    @staticmethod
    def refresh_access_token():
        params = {
            'client_id': Store.client_id,
            'client_secret': Store.client_secret,
            'grant_type': 'client_credentials'
        }
        if Store.access_token is None:
            r = requests.post('https://id.twitch.tv/oauth2/token', params=params)
            if r.status_code == 200:
                pp.pprint(r.json())
                Store.app_token = r.json()['access_token']
                Store.default_header['Authorization'] = f'Bearer {Store.app_token}'
                r = requests.get('https://api.twitch.tv/helix/webhooks/subscriptions', headers=Store.default_header)
                if r.status_code == 200:
                    pp.pprint(r.json())
        else:
            # refresh token
            pass

    @staticmethod
    def setup(configfile=None):
        print( configfile )
        if configfile is None:
            Store.slack_webhook = os.environ['SLACK_WEBHOOK']
            Store.client_id = os.environ['CLIENT_ID']
            Store.client_secret = os.environ['CLIENT_SECRET']
            Store.redirect_url = os.environ['REDIRECT_URL']
            Store.twitch_names = os.environ['TWITCH_NAMES'].split(',')
            Store.default_header['Client-ID'] = Store.client_id
        else:
            config = configparser.ConfigParser()
            config.optionxform = str
            config.read(configfile)
            Store.slack_webhook = config['DEFAULT']['SLACK_WEBHOOK_DEV']
            Store.client_id = config['DEFAULT']['CLIENT_ID']
            Store.client_secret = config['DEFAULT']['CLIENT_SECRET']
            Store.redirect_url = config['DEFAULT']['REDIRECT_URL']
            Store.twitch_names = config['DEFAULT']['TWITCH_NAMES'].split(',')
            Store.default_header['Client-ID'] = Store.client_id