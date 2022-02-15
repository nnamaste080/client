from json import JSONDecodeError
import json
import time
from turtle import pos
import requests


def get_config():
    f = open('config.json')
    try:
        data = json.load(f)
        return data
    except JSONDecodeError:
        print('check config.json File')


config = get_config()


def post_status():
    requests.post(config['host'] + '/getWorkerConnectionStatus',
                  data={'username': config['id']}
                  )


while True:
    time.sleep(1)
    post_status()
