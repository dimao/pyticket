import requests
from bs4 import BeautifulSoup


class Scrape:

    @staticmethod
    def scrape(url):
        url = url
        request = requests.get(url)
        content = request.content
        soup = BeautifulSoup(content, 'html.parser')
        element = soup.find('li', id='next_game')
        html_string = str(element.div.p)
        html_string = html_string.partition('<br/>')
        return html_string
