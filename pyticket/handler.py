import json
import logging
import os
import requests
from prometheus_client import Counter
from prometheus_client import Summary
from watchdog.events import PatternMatchingEventHandler
from zeep.settings import Settings
from zeep.transports import Transport

from pyticket.import_ticket import ImportTicket

wsdl = os.environ.get('WSDL_URL')
transport = Transport(timeout=10)
settings = Settings(strict=False)  # because of invalid xml response when calling UpdateEventSession
import_ticket = ImportTicket(wsdl, transport, settings)
import_ticket.client.service.GetCurrentVersion()

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

c = Counter('imported_file', 'File imported',
            ['filename'])
PROCESS_REQUEST_TIME = Summary('files_imported_total', 'Files imported total')
c1 = Counter('imported_barcode', 'Barcode imported', ['barcode'])

event = json.loads(requests.get(f"{os.environ.get('HOST_NAME')}:{int(os.environ.get('PORT'))}/get_event/").text)
next_game_place = json.loads(requests.get(f"{os.environ.get('HOST_NAME')}:{int(os.environ.get('PORT'))}/get_place").text)


class TicketsHandler(PatternMatchingEventHandler):

    @PROCESS_REQUEST_TIME.time()  # prometheus function execution time
    def process(self, fs_event):

        if dict(next_game_place)['next_game_place'] == '"Борисов-Арена"':
            logger.info(fs_event.src_path)
            with open(fs_event.src_path, 'r') as file:
                barcodes = file.readlines()
                for barcode_ in barcodes:
                    import_ticket.import_ticket(**event, barcode_=barcode_)
                    c.labels(filename=file.name).inc(1)
                    c1.labels(barcode=barcode_.rstrip()).inc(1)

    def on_created(self, fs_event):
        self.process(fs_event)
