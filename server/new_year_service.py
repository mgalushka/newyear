# -*- coding: utf-8 -*-

from threading import Timer

import json
import urllib2
import web


urls = (
    '/save-key', 'SaveKey',
    '/get-key', 'GetKey',
)
app = web.application(urls, globals())
keys = {}

class SaveKey:
    def __init__(self):
        pass

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        device = web.input()['device']
        key = web.input()['key']
        print('Storing key {0} for device {1}'.format(key, device))
        keys[device] = key
        return 'OK'


class GetKey:
    def __init__(self):
        pass

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        device = web.input()['device']
        if device not in keys:
            return 'ERROR'

        key = keys[device]
        print('Getting key for device {0}: {1}'.format(device, keys[device]))
        return key


def send_notification():
    """
    Sends notification to all users when New Year cames to corresponding country
    """
    print('Sending notification')
    # curl --header "Authorization: key=AIzaSyBOv9VWbm2kvUh60_Jdl3QusMYvm02DdfU"
    # --header Content-Type:"application/json" https://gcm-http.googleapis.com/gcm/send
    # -d "{\"registration_ids\":[\"APA91bGSSunCUhhp06i85-j1-JmZifSfFgc50EgohKZWlPtM6CflwPbuGSWCgN-8SlnaxbRM26GvaXWYLvZIkgeFTYrD1VFAgfR3oi91Y2N58CPEmONIgOZqnawyPs2aSCsMjGcR1egg\"],\"data\":{\"text\":\"Ukraine\"}}"

    data = {
        'registration_ids': ['APA91bGSSunCUhhp06i85-j1-JmZifSfFgc50EgohKZWlPtM6CflwPbuGSWCgN-8SlnaxbRM26GvaXWYLvZIkgeFTYrD1VFAgfR3oi91Y2N58CPEmONIgOZqnawyPs2aSCsMjGcR1egg'],
        'data': {'text': 'Ukraine'},
    }
    req = urllib2.Request(
        'https://gcm-http.googleapis.com/gcm/send',
        json.dumps(data),
        {
            'Content-Type': 'application/json',
            'Authorization': 'key=AIzaSyBOv9VWbm2kvUh60_Jdl3QusMYvm02DdfU',
        },
    )

    response = urllib2.urlopen(req)
    the_page = response.read()

    print(the_page)

    # schedule itself
    t = Timer(30.0, send_notification)
    t.start()

if __name__ == '__main__':
    # scheduling timer
    send_notification()
    app.run()