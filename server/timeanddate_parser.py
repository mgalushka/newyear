from bs4 import BeautifulSoup

if __name__ == '__main__':
    f = open('/Users/mgalushka/Downloads/times.txt', 'r')
    all = f.read()

    soup = BeautifulSoup(all, 'html.parser')

    for tr in soup.table.tbody:
        countries_tr = tr.find_all('td')[2]
        countries_txt = countries_tr.span['title'] \
            if countries_tr.span else countries_tr.text

        countries = countries_txt \
            .replace('regions of', '') \
            .replace('with exceptions', '') \
            .replace(' and', ',') \
            .replace('most of', '') \
            .replace('some regions of', '') \
            .replace(' some', '') \
            .replace('small region of', '') \
            .replace('much of', '') \
            .replace(' , ', ',') \
            .replace(', ', ',') \
            .replace(' ,', ',') \
            .replace('/', ',') \
            .replace('U.S.A.', 'USA')
        print(u'\'{0}\'\t\'{1}\',\t\'{2}\''.format(
            countries_txt,
            countries,
            ','.join(x.text for x in tr.find_all('td')[3].find_all('a'))))
