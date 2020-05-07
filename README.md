# twitch-notify-slackbot

This is a simple tool for tracking certain users on Twitch and notifying a Slack channel when they are live. It uses the Twitch "helix" API. Webhooks are used for finding when users go live and for sending messages to Slack.


## Environment variables

This tool is mean to be run as a Docker container and expects certain enivrunment variables to be set as part of the `docker run` command

### Twitch users to follow

`TWITCH_NAMES` usernames of Twitch users to follow, separated by commas

### Working with the Twitch API

These values can be found and should match the settings for your registered Twtich app. (see: https://dev.twitch.tv/console/apps)

`CLIENT_ID` Client ID for your Twitch app 

`CLIENT_SECRET` Client Secret for your Twitch app 

`REDIRECT_URL` URL that Twitch will use

### Working with Slack

`SLACK_WEBHOOK` Slack webhook URL, used to send messages to a specific Slack server+channel
