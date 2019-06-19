import locale
import requests
from datetime import datetime
from bs4 import BeautifulSoup


class Scrape:
    def __init__(self, locale_, url):
        self.locale = locale
        self.url = url
        locale.setlocale(locale.LC_ALL, locale_)  # set locale for Russian month
        request = requests.get(url)
        content = request.content
        soup = BeautifulSoup(content, 'html.parser')
        element = soup.find('li', id='next_game')
        self.html_string = str(element.div.p)
        self.html_string = self.html_string.partition('<br/>')
        self.next_game_date_string = self.html_string[0].strip('<p>\t')
        self.next_game_datetime = datetime.strptime(self.next_game_date_string, '%d %B %Y, %H:%M')

    def get_session_start(self):
        session_start = self.next_game_datetime.replace(hour=self.next_game_datetime.hour - 3)
        session_start = session_start.strftime('%d%m%Y%H%M')
        return session_start

    def get_session_end(self):
        session_end = self.next_game_datetime.replace(hour=self.next_game_datetime.hour + 3)
        session_end = session_end.strftime('%d%m%Y%H%M')
        return session_end

    def get_event_code(self):
        return self.next_game_datetime.strftime('%d%m%y')

    def get_event_name(self):
        return self.next_game_date_string

    def get_next_game_place(self):
        next_game_place = self.html_string[2].strip(' </p>')
        return next_game_place
