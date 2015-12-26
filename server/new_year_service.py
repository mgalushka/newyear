# -*- coding: utf-8 -*-

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


if __name__ == '__main__':
    app.run()