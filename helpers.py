import requests
import pprint as pp
import os

def get_game(game_id):
    if not game_id:
        return { 'name': '_unknown game_' }
    params = { 'id': game_id }
    r = requests.get('https://api.twitch.tv/helix/games', headers={ 'Client-ID': CLIENT_ID }, params=params)
    pp.pprint(r.json())
    
    game = r.json()['data'][0]
    return game

def get_tags(tag_ids, locale="en-us"): # unused
    tag_count = len(tag_ids)
    params = {
        'tag_id': "&".join(tag_ids),
        'first': tag_count
    }
    r = requests.get('https://api.twitch.tv/helix/tags/streams', headers={ 'Client-ID': CLIENT_ID }, params=params)
    pp.pprint(r.json())
    return ["tag1", "tag2"]

def get_stream_tags(broadcaster_id, locale="en-us"): # unused
    params = { 'broadcaster_id': broadcaster_id }
    r = requests.get('https://api.twitch.tv/helix/streams/tags', headers={ 'Client-ID': CLIENT_ID }, params=params)
    data = r.json()['data']
    pp.pprint(data)
    if data:
        return ['Example1', 'Example2', 'Example3']
    else:
        return ['example1', 'example2', 'example3']

def size_image(url, width, height):
    return url.replace('{width}', str(width)).replace('{height}', str(height))

def make_stream(data):
    global CLIENT_ID
    CLIENT_ID = os.environ['CLIENT_ID']
    print(data.keys())
    stream = {}
    stream['title'] = data['title']
    stream['game'] = get_game(data['game_id'])
    stream['thumbnail_url'] = size_image(data['thumbnail_url'], 640,360)
    return stream

def make_message_legacy(the_color='#ff8000'): # unused
    return {
        "text": "some message",
        "attachments": [
            {
                "fallback": "Plain-text summary of the attachment.",
                "color": the_color,
                "pretext": "Optional text that appears above the attachment block",
                "author_name": "Bobby Tables",
                "author_link": "http://flickr.com/bobby/",
                "author_icon": "http://flickr.com/icons/bobby.jpg",
                "title": "Slack API Documentation",
                "title_link": "https://api.slack.com/",
                "text": "Optional text that appears within the attachment",
                "fields": [
                    {
                        "title": "Priority",
                        "value": "High",
                        "short": False
                    }
                ],
                "image_url": "http://my-website.com/path/to/image.jpg",
                "thumb_url": "http://example.com/path/to/thumb.png",
                "footer": "Slack API",
                "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                "ts": 123456789
            }
        ]
    }

def make_message(user, stream):
    return  {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{user.display_name}* is LIVE!"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{stream['title']}*\nPlaying: {stream['game']['name']}\n\n:movie_camera:\t:movie_camera:\t:movie_camera:"
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": user.profile_image,
                            "alt_text": f"{user.display_name}'s profile picture"
                        }
                    },
                    {
                        "type": "actions",
                        "block_id": "actionblock789",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Watch now!"
                                },
                                "style": "primary",
                                "url": f"https://www.twitch.tv/{user.display_name.lower()}"
                            }
                        ]
                    },
                    {
                        "type": "image",
                        "title": {
                            "type": "plain_text",
                            "text": "Stream Preview"
                        },
                        "image_url": stream['thumbnail_url'],
                        "alt_text": f"{user.display_name}'s stream preview"
                    }
                ]
            }
