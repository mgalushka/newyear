# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from threading import Timer

import json
import urllib2
import web

# new year schedule: time -> freeform list of countries, list of countries, list of cities
schedule = [
    ['-14:00','Samoa and Christmas Island/Kiribati','Samoa,Christmas Island,Kiribati','Kiritimati,Apia,Salelologa (Savai\'i)'],
    ['-13:45','Chatham Islands/New Zealand','Chatham Islands,New Zealand','Chatham Islands'],
    ['-13:00','New Zealand with exceptions, Fiji, some regions of Antarctica, Tonga, Phoenix Islands/Kiribati and Tokelau','New Zealand,Fiji, Antarctica,Tonga,Phoenix Islands,Kiribati,Tokelau','Auckland,Suva,Wellington,Nukualofa'],
    ['-12:00','small region of Russia, regions of Kiribati, Marshall Islands, Wallis and Futuna, Nauru, regions of US Minor Outlying Islands and Tuvalu',' Russia, Kiribati,Marshall Islands,Wallis,Futuna,Nauru, US Minor Outlying Islands,Tuvalu','Anadyr,Funafuti,Yaren,Tarawa,Majuro'],
    ['-11:30','much of Australia, Sakha (Yakutia)/Russia, Pohnpei/Micronesia, Vanuatu, some regions of Antarctica, Bougainville/Papua New Guinea, Solomon Islands, New Caledonia and Norfolk Island',' Australia,Sakha (Yakutia),Russia,Pohnpei,Micronesia,Vanuatu, Antarctica,Bougainville,Papua New Guinea,Solomon Islands,New Caledonia,Norfolk Island','Melbourne,Sydney,Canberra,Honiara'],
    ['-11:00','small region of Australia',' Australia','Adelaide,Broken Hill,Ceduna'],
    ['-10:30','Queensland/Australia, some regions of Russia, much of Papua New Guinea, regions of Micronesia, Northern Mariana Islands, small region of Antarctica and Guam','Queensland,Australia, Russia, Papua New Guinea, Micronesia,Northern Mariana Islands, Antarctica,Guam','Brisbane,Port Moresby,Hagåtña'],
    ['-10:00','Northern Territory/Australia','Northern Territory,Australia','Darwin,Alice Springs,Tennant Creek'],
    ['-9:30','Japan, South Korea, Sakha (Yakutia)/Russia, small region of Indonesia, Timor-Leste and Palau','Japan,South Korea,Sakha (Yakutia),Russia, Indonesia,Timor-Leste,Palau','Tokyo,Seoul,Dili,Melekeok,Yakutsk'],
    ['-9:00','Western Australia/Australia','Western Australia,Australia','Eucla'],
    ['-8:45','North Korea','North Korea','Pyongyang,Hamhung,Chongjin,Namp’o'],
    ['-8:00','China, Philippines, regions of Indonesia, Western Australia/Australia, Malaysia, most of Mongolia, Taiwan, small region of Russia, Brunei, Hong Kong, Singapore and Macau','China,Philippines, Indonesia,Western Australia,Australia,Malaysia, Mongolia,Taiwan, Russia,Brunei,Hong Kong,Singapore,Macau','Beijing,Hong Kong,Manila,Singapore'],
    ['-7:00','much of Indonesia, Thailand, Krasnoyarsk/Russia, Vietnam, Cambodia, Laos, some regions of Mongolia, small region of Antarctica and Christmas Island',' Indonesia,Thailand,Krasnoyarsk,Russia,Vietnam,Cambodia,Laos, Mongolia, Antarctica,Christmas Island','Jakarta,Bangkok,Hanoi,Phnom Penh'],
    ['-6:30','Myanmar and Cocos Islands','Myanmar,Cocos Islands','Yangon,Naypyidaw,Mandalay,Mawlamyine'],
    ['-6:00','Bangladesh, much of Kazakhstan, small region of Russia, Kyrgyzstan, Bhutan, British Indian Ocean Territory and small region of Antarctica','Bangladesh, Kazakhstan, Russia,Kyrgyzstan,Bhutan,British Indian Ocean Territory, Antarctica','Dhaka,Almaty,Bishkek,Thimphu,Astana'],
    ['-5:45','Nepal','Nepal','Kathmandu,Biratnagar,Pokhara'],
    ['-5:30','India and Sri Lanka','India,Sri Lanka','New Delhi,Mumbai,Kolkata,Bengaluru'],
    ['-5:00','Pakistan, some regions of Russia, Uzbekistan, Turkmenistan, regions of Kazakhstan, Maldives, Tajikistan, French Southern Territories and small region of Antarctica','Pakistan, Russia,Uzbekistan,Turkmenistan, Kazakhstan,Maldives,Tajikistan,French Southern Territories, Antarctica','Tashkent,Islamabad,Lahore,Karachi'],
    ['-4:30','Afghanistan','Afghanistan','Kabul,Kandahar,Mazari Sharif,Herat'],
    ['-4:00','Azerbaijan, United Arab Emirates, Armenia, Oman, small region of Russia, much of Georgia, Reunion (French), Mauritius and Seychelles','Azerbaijan,United Arab Emirates,Armenia,Oman, Russia, Georgia,Reunion (French),Mauritius,Seychelles','Dubai,Abu Dhabi,Muscat,Port Louis'],
    ['-3:30','Iran','Iran','Tehran,Rasht,Esfahãn,Mashhad,Tabriz'],
    ['-3:00','Moscow/Russia, Saudi Arabia, Ethiopia, Iraq, Belarus, Somalia, Madagascar, Tanzania, Eritrea, Uganda, regions of Ukraine, Djibouti, Sudan, Yemen, Kenya, South Sudan, Qatar, Comoros, Bahrain, regions of Georgia, small region of South Africa, Kuwait and Mayotte','Moscow,Russia,Saudi Arabia,Ethiopia,Iraq,Belarus,Somalia,Madagascar,Tanzania,Eritrea,Uganda, Ukraine,Djibouti,Sudan,Yemen,Kenya,South Sudan,Qatar,Comoros,Bahrain, Georgia, South Africa,Kuwait,Mayotte','Moscow,Baghdad,Khartoum,Nairobi'],
    ['-2:00','Greece, South Africa with exceptions, Finland, Israel, Turkey, Egypt, Kyiv/Ukraine, Botswana, Bulgaria, Romania, Estonia, Palestinian Territories, Syria, Zambia, Zimbabwe, Latvia, much of Dem. Rep. Congo, Libya, Jordan, Burundi, Cyprus, Rwanda, Malawi, Namibia, Lebanon, Lithuania, Mozambique, Lesotho, Moldova, Swaziland and small region of Russia','Greece,South Africa,Finland,Israel,Turkey,Egypt,Kyiv,Ukraine,Botswana,Bulgaria,Romania,Estonia,Palestinian Territories,Syria,Zambia,Zimbabwe,Latvia, Dem. Rep. Congo,Libya,Jordan,Burundi,Cyprus,Rwanda,Malawi,Namibia,Lebanon,Lithuania,Mozambique,Lesotho,Moldova,Swaziland, Russia','Cairo,Ankara,Athens,Bucharest'],
    ['-1:00','Germany, Norway, Switzerland, Austria, France, Poland, Italy, Barcelona/Spain, Netherlands, Sweden, Nigeria, Denmark, Belgium, Croatia, Bosnia-Herzegovina, Algeria, Tunisia, Czech Republic, Slovakia, Angola, Chad, Central African Republic, Hungary, Benin, Cameroon, Equatorial Guinea, Albania, Serbia, regions of Dem. Rep. Congo, Slovenia, Niger, Congo, Luxembourg, Macedonia, Republic of, Kosovo, Montenegro, Gabon, San Marino, Malta, Liechtenstein, Vatican City State, Gibraltar, Monaco and Andorra','Germany,Norway,Switzerland,Austria,France,Poland,Italy,Barcelona,Spain,Netherlands,Sweden,Nigeria,Denmark,Belgium,Croatia,Bosnia-Herzegovina,Algeria,Tunisia,Czech Republic,Slovakia,Angola,Chad,Central African Republic,Hungary,Benin,Cameroon,Equatorial Guinea,Albania,Serbia, Dem. Rep. Congo,Slovenia,Niger,Congo,Luxembourg,Macedonia,Republic of,Kosovo,Montenegro,Gabon,San Marino,Malta,Liechtenstein,Vatican City State,Gibraltar,Monaco,Andorra','Brussels,Madrid,Paris,Rome,Algiers'],
    ['0:00','United Kingdom, Portugal with exceptions, Ireland, Cote d\'Ivoire (Ivory Coast), Morocco, Iceland, Burkina Faso, Senegal, Sierra Leone, Togo, Liberia, Mauritania, Western Sahara, Guinea, Mali, some regions of Spain, Guinea-Bissau, Saint Helena, Gambia, Ghana, Guernsey, some regions of Antarctica, Isle of Man, small region of Greenland, Faroe Islands, Sao Tome and Principe and Jersey','United Kingdom,Portugal,Ireland,Cote d\'Ivoire (Ivory Coast),Morocco,Iceland,Burkina Faso,Senegal,Sierra Leone,Togo,Liberia,Mauritania,Western Sahara,Guinea,Mali, Spain,Guinea-Bissau,Saint Helena,Gambia,Ghana,Guernsey, Antarctica,Isle of Man, Greenland,Faroe Islands,Sao Tome,Principe,Jersey','London,Casablanca,Dublin,Lisbon,Accra'],
    ['1:00','Cabo Verde, Azores/Portugal and small region of Greenland','Cabo Verde,Azores,Portugal, Greenland','Praia,Ponta Delgada,Ittoqqortoormiit'],
    ['2:00','regions of Brazil and South Georgia/Sandwich Is.',' Brazil,South Georgia,Sandwich Is.','Rio de Janeiro,São Paulo,Brasilia'],
    ['3:00','Argentina, regions of Brazil, Chile with exceptions, Uruguay, most of Greenland, regions of Antarctica, Paraguay, French Guiana, Suriname, Falkland Islands and Saint Pierre and Miquelon','Argentina, Brazil,Chile,Uruguay, Greenland, Antarctica,Paraguay,French Guiana,Suriname,Falkland Islands,Saint Pierre,Miquelon','Buenos Aires,Santiago,Asuncion'],
    ['3:30','Newfoundland and Labrador/Canada','Newfoundland,Labrador,Canada','St. John\'s,Mary\'s Harbour'],
    ['4:00','some regions of Canada, Bolivia, Dominican Republic, Amazonas/Brazil, Puerto Rico, Trinidad and Tobago, US Virgin Islands, Turks and Caicos Islands, Guyana, Caribbean Netherlands, Antigua and Barbuda, Guadeloupe, Saint Kitts and Nevis, Saint Lucia, British Virgin Islands, small region of Greenland, Saint Vincent and Grenadines, Bermuda, Anguilla, Dominica, Montserrat, Sint Maarten, Barbados, Saint Martin, Grenada, Saint Barthélemy, Curaçao, Aruba and Martinique','some  Canada,Bolivia,Dominican Republic,Amazonas,Brazil,Puerto Rico,Trinidad,Tobago,US Virgin Islands,Turks,Caicos Islands,Guyana,Caribbean Netherlands,Antigua,Barbuda,Guadeloupe,Saint Kitts,Nevis,Saint Lucia,British Virgin Islands, Greenland,Saint Vincent,Grenadines,Bermuda,Anguilla,Dominica,Montserrat,Sint Maarten,Barbados,Saint Martin,Grenada,Saint Barthélemy,Curaçao,Aruba,Martinique','La Paz,San Juan,Santo Domingo,Halifax'],
    ['4:30','Venezuela','Venezuela','Caracas,Barquisimeto,Maracaibo'],
    ['5:00','regions of U.S.A., regions of Canada, Colombia, Peru, Ecuador with exceptions, Cuba, Panama, small region of Brazil, small region of Mexico, Haiti, Jamaica, Bahamas, small region of Chile and Cayman Islands',' USA, Canada,Colombia,Peru,Ecuador,Cuba,Panama, Brazil, Mexico,Haiti,Jamaica,Bahamas, Chile,Cayman Islands','New York,Washington DC,Detroit,Havana'],
    ['6:00','regions of U.S.A., Federal District/Mexico, some regions of Canada, Honduras, Belize, Nicaragua, Costa Rica, El Salvador, Guatemala and small region of Ecuador',' USA,Federal District,Mexico, Canada,Honduras,Belize,Nicaragua,Costa Rica,El Salvador,Guatemala, Ecuador','Mexico City,Chicago,Guatemala,Dallas'],
    ['7:00','some regions of U.S.A., some regions of Canada and some regions of Mexico','some  USA, Canada, Mexico','Calgary,Denver,Edmonton,Phoenix'],
    ['8:00','regions of U.S.A., some regions of Canada, Baja California/Mexico and Pitcairn Islands',' USA, Canada,Baja California,Mexico,Pitcairn Islands','Los Angeles,San Francisco,Las Vegas'],
    ['9:00','Alaska/U.S.A. and regions of French Polynesia','Alaska,USA, French Polynesia','Anchorage,Fairbanks,Juneau,Unalaska'],
    ['9:30','Marquesas Islands/French Polynesia','Marquesas Islands,French Polynesia','Taiohae'],
    ['10:00','small region of U.S.A., Tahiti/French Polynesia and Cook Islands',' USA,Tahiti,French Polynesia,Cook Islands','Honolulu,Rarotonga,Adak,Papeete,Hilo'],
    ['11:00','American Samoa, regions of US Minor Outlying Islands and Niue','American Samoa, US Minor Outlying Islands,Niue','Alofi,Midway,Pago Pago'],
    ['12:00','much of US Minor Outlying Islands',' US Minor Outlying Islands','Baker Island,Howland Island'],
    ['-101:40', 'Test message', 'Ukraine', 'Kiev'],
]

urls = (
    '/save-key', 'SaveKey',
    '/get-key', 'GetKey',
    '/list', 'ListKeys',
    '/send-debug', 'SendDebug',
)
app = web.application(urls, globals())
web.keys = {}


class SaveKey:
    def __init__(self):
        pass

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        device = web.input()['device']
        key = web.input()['key']
        print('Storing key {0} for device {1}'.format(key, device))
        web.keys[device] = key
        return 'OK'


class GetKey:
    def __init__(self):
        pass

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        device = web.input()['device']
        if device not in web.keys:
            return 'ERROR'

        key = web.keys[device]
        print('Getting key for device {0}: {1}'.format(device, key))
        return key


class ListKeys:
    def __init__(self):
        pass

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        return json.dumps(web.keys)


class SendDebug:
    def __init__(self):
        pass

    def POST(self):
        web.header('Access-Control-Allow-Origin', '*')
        send_notification('Default message')
        return 'OK'


def send_notification(freeform, countries, cities):
    print(web.keys)
    if not web.keys:
        print('Empty keys map - nothing to send. '
              'Skip notifications sending step.')
        return

    data = {
        'registration_ids': web.keys.values(),
        'data': {
            'text': 'New Year came to: {0}'.format(freeform),
            'countries': countries,
            'cities': cities,
        },
    }
    print('Sending: {0}'.format(json.dumps(data)))
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
        freeform = s_values[1]
        countries = s_values[2]
        cities = s_values[3]

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
            args=[freeform, countries, cities],
        )
        t.start()


if __name__ == '__main__':
    # scheduling timer
    schedule_notifications()
    app.run()
