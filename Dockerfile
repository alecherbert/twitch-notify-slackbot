FROM python:3.8-buster

RUN git clone https://github.com/alecherbert/twitch-notify-slackbot.git twitch-notifier
RUN python -m pip install -r twitch-notifier/requirements.txt

ENTRYPOINT ["python", "twitch-notifier/twitch-notifier.py"]