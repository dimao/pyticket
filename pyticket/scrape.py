import requests
import sys
import arrow
import logging
from bs4 import BeautifulSoup


class Scrape:
    def __init__(self, url):
        self.logger = logging.getLogger('scrape')
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.setLevel(logging.INFO)

        self.url = url
        request = requests.get(url)
        content = request.content
        soup = BeautifulSoup(content, 'html.parser')
        element = soup.find('li', id='next_game')
        self.html_string = str(element.div.p)
        self.html_string = self.html_string.partition('<br/>')
        self.next_game_date_string = self.html_string[0].strip('<p>\t')
        self.next_game_datetime = arrow.get(self.next_game_date_string, 'DD MMMM YYYY, HH:mm', locale='ru')

    def get_session_start(self):
        session_start = self.next_game_datetime.shift(hours=-3)
        session_start = session_start.format('DDMMYYYYHHmm')
        self.logger.info(f'session_start: {session_start}')
        return session_start

    def get_session_end(self):
        session_end = self.next_game_datetime.shift(hours=+3)
        session_end = session_end.format('DDMMYYYYHHmm')
        self.logger.info(f'session_end: {session_end}')
        return session_end

    def get_event_code(self):
        self.logger.info(f'event_code: {self.next_game_datetime.format("DMMYY")}')
        return self.next_game_datetime.format('DMMYY')

    def get_event_name(self):
        return self.next_game_date_string

    def get_next_game_place(self):
        next_game_place = self.html_string[2].strip(' </p>')
        return next_game_place
