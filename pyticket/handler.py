import json
import logging
import sys

import arrow
from prometheus_client import Counter
from prometheus_client import Summary
from watchdog.events import PatternMatchingEventHandler
from zeep.settings import Settings
from zeep.transports import Transport

from import_ticket import ImportTicket
from scrape import Scrape

with open('config.json', 'r') as f:
    config = json.load(f)

wsdl = config['wsdl']['url']
transport = Transport(timeout=10)
settings = Settings(strict=False)  # because of invalid xml response when calling UpdateEventSession
import_ticket = ImportTicket(wsdl, transport, settings)
import_ticket.client.service.GetCurrentVersion()

logger = logging.getLogger('handler')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

c = Counter('import_tickets_total', 'Imported tickets',
            ['next_game_place_label', 'event_code_label', 'filename_label', 'barcode_label'])
PROCESS_REQUEST_TIME = Summary('import_request_processing_seconds', 'Import time spent processing request')
SCRAPE_REQUEST_TIME = Summary('scrape_request_processing_seconds', 'Scrape time spent processing request')


class TicketsHandler(PatternMatchingEventHandler):

    patterns = config['game']['patterns']
    site_url = config['site']['url']
    time_shift = int(config['game']['time_shift'])

    session_start = ''
    session_end = ''
    next_game_place = ''
    event_code = ''
    event_name = ''
    next_game_datetime = ''

    @SCRAPE_REQUEST_TIME.time()
    def scrape(self):
        html_string = Scrape.scrape(self.site_url)
        next_game_date_string = html_string[0].strip('<p>\t')
        self.next_game_datetime = arrow.get(next_game_date_string, 'DD MMMM YYYY, HH:mm', locale='ru')
        self.session_start = self.next_game_datetime.shift(hours=-self.time_shift).format('DDMMYYYYHHmm')
        self.session_end = self.next_game_datetime.shift(hours=+self.time_shift).format('DDMMYYYYHHmm')
        self.event_code = self.next_game_datetime.format('DMMYY')
        self.event_name = next_game_date_string
        self.next_game_place = html_string[2].strip(' </p>')
        print('-' * 87)
        logger.info(f'Scraping next_game_datetime: \033[1m{self.next_game_datetime}\033[0m')
        print('-' * 87)

    @PROCESS_REQUEST_TIME.time()  # prometheus function execution time
    def process(self, event):

        if self.next_game_place != '"Борисов-Арена"':  # TODO: change this to ==
            logger.info(event.src_path)
            with open(event.src_path, 'r') as file:
                barcodes = file.readlines()
                for barcode_ in barcodes:
                    import_ticket.import_ticket(self.event_code, self.session_start,
                                                self.session_end,
                                                self.event_name, barcode_)

                    c.labels(next_game_place_label=self.next_game_place,
                             event_code_label=self.event_code, filename_label=event.src_path,
                             barcode_label=barcode_.rstrip()).inc(1)

    def on_created(self, event):
        self.process(event)
