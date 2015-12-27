# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
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

# new year schedule: time -> list of countries
schedule = [
    ['-14:00', 'Christmas Island/Kiribati and Samoa', 'Kiritimati Apia'],
    ['-13:45', 'Chatham Islands/New Zealand', 'Chatham Islands'],
    ['-13:00', 'New Zealand with exceptions and 5 more',
     'Auckland Suva Wellington Nukualofa'],
    ['-12:00', 'small region of Russia Marshall Islands and 5 more',
     'Anadyr Funafuti Yaren Tarawa'],
    ['-11:30', 'Norfolk Island', 'Kingston'],
    ['-11:00', 'much of Australia and 5 more',
     ' Melbourne Sydney Canberra Honiara'],
    ['-10:30', 'small region of Australia', 'Adelaide Broken Hill'],
    ['-10:00',
     'Queensland/Australia and 5 more Brisbane', 'Port Moresby Guam (Hagatna) Cairns'],
    ['-9:30', 'Northern Territory/Australia', ' Darwin Alice Springs Uluru'],
    ['-9:00', 'Japan and 6 more', 'Tokyo Seoul Pyongyang Dili'],
    ['-8:45', 'Western Australia/Australia', 'Eucla'],
    ['-8:00', 'China and 12 more', 'Beijing Hong Kong Manila Singapore'],
    ['-7:00', 'much of Indonesia Thailand and 7 more',
     'Jakarta Bangkok Hanoi Phnom Penh'],
    ['-6:30', 'Myanmar and Cocos Islands', 'Yangon Naypyidaw Mandalay Bantam'],
    ['-6:00', 'Bangladesh some regions of Russia and 4 more',
     ' Dhaka Almaty Bishkek Thimphu'],
    ['-5:45', 'Nepal', 'Kathmandu Biratnagar Pokhara'],
    ['-5:30', 'India and Sri Lanka', 'New Delhi Mumbai Kolkata Bangalore'],
    ['-5:00', 'Pakistan and 8 more', 'Tashkent Islamabad Lahore Karachi'],
    ['-4:30', 'Afghanistan', 'Kabul Kandahar Mazari Sharif Herat'],
    ['-4:00', 'much of Russia and 8 more', 'Moscow Dubai Abu Dhabi Muscat'],
    ['-3:30', 'Iran', ' Tehran Rasht Esfahan Bandar-Abbas'],
    ['-3:00', 'Iraq and 20 more', ' Baghdad Khartoum Nairobi Addis Ababa'],
    ['-2:00', 'Greece and 30 more', 'Cairo Ankara Athens Bucharest'],
    ['-1:00', 'Germany and 43 more', 'Brussels Madrid Paris Rome'],
    ['0:00', 'United Kingdom and 24 more', 'London Casablanca Dublin Lisbon'],
    ['1:00',
     'Cape Verde some regions of Greenland and 1 more', 'Praia Ponta Delgada (Azores) Ittoqqortoormiit Mindelo'],
    ['2:00', 'regions of Brazil Uruguay and 1 more',
     ' Rio de Janeiro Sao Paulo Brasilia Montevideo'],
    ['3:00',
     'regions of Brazil Argentina and 7 more', 'Buenos Aires Santiago Asuncion Paramaribo'],
    ['3:30', 'Newfoundland and Labrador/Canada',
     ' St. John\'s Conception Bay South Corner Brook Gander'],
    [
        '4:00', 'some regions of Canada and 26 more',
        'La Paz San Juan Santo Domingo Halifax'],
    ['4:30', 'Venezuela', 'Caracas Barquisimeto Maracaibo Maracay'],
    ['5:00', 'regions of U.S.A. regions of Canada and 12 more',
     'New York Washington DC Detroit Havana'],
    ['6:00', 'regions of U.S.A. some regions of Canada and 8 more',
     'Mexico City Chicago Guatemala Dallas'],
    ['7:00', 'some regions of U.S.A. some regions of Canada and 1 more',
     ' Calgary Denver Edmonton Phoenix'],
    ['8:00', 'regions of U.S.A. some regions of Canada and 2 more',
     'Los Angeles San Francisco Las Vegas Seattle'],
    ['9:00', 'Alaska/U.S.A. and French Polynesia',
     'Anchorage Fairbanks Unalaska Juneau'],
    ['9:30', 'Marquesas Islands/France', ' Taiohae'],
    ['10:00', 'small region of U.S.A. and 2 more',
     'Honolulu Rarotonga Adak Papeete'],
    ['11:00', 'American Samoa Midway Atoll/U.S.A. and 1 more',
     'Alofi Midway Pago Pago'],
    ['12:00', 'small region of U.S.A.', 'Baker Island Howland Island'],
    ['-102:55', 'Test', 'Test'],
]


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


def send_notification(text):
    if not keys:
        print('Empty keys map - nothing to send. '
              'Skip notifications sending step.')
        return

    data = {
        'registration_ids': [keys.values()],
        'data': {'text': text},
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


def schedule_notifications():
    """
    Sends notification to all users when New Year cames to corresponding country
    """
    print('Scheduling all notifications according to schedule')
    # curl --header "Authorization: key=AIzaSyBOv9VWbm2kvUh60_Jdl3QusMYvm02DdfU"
    # --header Content-Type:"application/json" https://gcm-http.googleapis.com/gcm/send
    # -d "{\"registration_ids\":[\"APA91bGSSunCUhhp06i85-j1-JmZifSfFgc50EgohKZWlPtM6CflwPbuGSWCgN-8SlnaxbRM26GvaXWYLvZIkgeFTYrD1VFAgfR3oi91Y2N58CPEmONIgOZqnawyPs2aSCsMjGcR1egg\"],\"data\":{\"text\":\"Ukraine\"}}"

    now = datetime.now()

    # next year
    year = datetime.today().year + 1
    midnight = datetime.strptime(
        '{0}-01-01 00:00'.format(year),
        '%Y-%m-%d %H:%M',
    )

    for s_values in schedule:
        shift = s_values[0]
        countries = s_values[1]
        cities = s_values[2]

        hours = int(shift[:shift.find(':')])
        minutes = -int(shift[shift.find(':') + 1:])
        run_at = midnight + timedelta(hours=hours, minutes=minutes)

        delay = (run_at - now).total_seconds()
        text = '{0}, {1}'.format(countries, cities)

        print('Scheduling notifications at {0} with text: {1}'.format(
            run_at,
            text,
        ))
        t = Timer(
            delay,
            send_notification,
            args=[text],
        )
        t.start()


if __name__ == '__main__':
    # scheduling timer
    schedule_notifications()
    app.run()
