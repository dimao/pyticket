import sys
import logging
import arrow
from datetime import datetime
from datetime import timedelta
from wsgiref.simple_server import make_server

from prometheus_client import Counter
from prometheus_client import Summary
from prometheus_client import make_wsgi_app
from timeloop import Timeloop
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from zeep.settings import Settings
from zeep.transports import Transport

from import_ticket import ImportTicket
from scrape import Scrape

wsdl = 'http://10.0.7.8:8090/GnrtBT6NetWcfServiceLibrary.GnrtBT6NetWcfService/?wsdl'
transport = Transport(timeout=10)
settings = Settings(strict=False)  # because of invalid xml response when calling UpdateEventSession
import_ticket = ImportTicket(wsdl, transport, settings)

c = Counter('import_tickets_total', 'Imported tickets',
            ['next_game_place_label', 'event_code_label', 'filename_label', 'barcode_label'])
PROCESS_REQUEST_TIME = Summary('process_request_processing_seconds', 'Process time spent processing request')
SCRAPE_REQUEST_TIME = Summary('scrape_request_processing_seconds', 'Scrape time spent processing request')


class TicketsHandler(PatternMatchingEventHandler):
    patterns = ["*.txt"]

    logger = logging.getLogger('main')
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)

    session_start = ''
    session_end = ''
    next_game_place = ''
    event_code = ''
    event_name = ''
    next_game_datetime = arrow.utcnow().format('YYYY-MM-DD HH:mm:ss')
    logger.info(f'Initial next_game_datetime: \033[1m{next_game_datetime}\033[0m')

    @SCRAPE_REQUEST_TIME.time()
    def scrape(self):
        scrape = Scrape('https://fcbate.by/fan-zone')
        # scrape = Scrape("ru_RU.UTF-8", 'http://dimao')
        self.next_game_datetime = scrape.next_game_datetime
        self.session_start = scrape.get_session_start()
        self.session_end = scrape.get_session_end()
        self.next_game_place = scrape.get_next_game_place()
        self.event_code = scrape.get_event_code()
        self.event_name = scrape.get_event_name()
        print('-' * 87)
        self.logger.info(f'Scraping next_game_datetime: \033[1m{self.next_game_datetime}\033[0m')
        print('-' * 87)

    @PROCESS_REQUEST_TIME.time()  # prometheus function execution time
    def process(self, event):
        """
                        event.event_type
                            'modified' | 'created' | 'moved' | 'deleted'
                        event.is_directory
                            True | False
                        event.src_path
                            path/to/observed/file
                        """

        if datetime.now() < self.next_game_datetime and self.next_game_place == '"Борисов-Арена"':  # TODO: change this to ==
            self.logger.info(event.src_path)
            # print(event.src_path)
            with open(event.src_path, 'r') as file:
                barcodes = file.readlines()
                for barcode_ in barcodes:
                    # print(barcode_.rstrip())
                    import_ticket.import_ticket(self.event_code, self.session_start,
                                                self.session_end,
                                                self.event_name, barcode_)

                    c.labels(next_game_place_label=self.next_game_place,
                             event_code_label=self.event_code, filename_label=event.src_path,
                             barcode_label=barcode_.rstrip()).inc(1)

    def on_created(self, event):
        self.process(event)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args:
        path = args[0]
        # scrape_interval = args[1]
        # print(path)
        # print(scrape_interval)
    else:
        path = '.'
        # scrape_interval = 3600

    observer = Observer()
    tickets_handler = TicketsHandler()
    timeloop = Timeloop()


    @timeloop.job(interval=timedelta(seconds=int(10)))  # scraping interval
    def timeloop_job():
        tickets_handler.scrape()


    timeloop.start()  # start timeloop thread

    observer.schedule(tickets_handler, path=path, recursive=False)
    tickets_handler.logger.info(f'Monitoring {path} directory with seconds interval')
    observer.start()

    metrics_app = make_wsgi_app()


    def prom_app(environ, start_fn):
        if environ['PATH_INFO'] == '/metrics':
            return metrics_app(environ, start_fn)
        start_fn('200 OK', [])
        return [b'<a href="http://localhost:8000/metrics">metrics<a>']


    try:
        httpd = make_server('0.0.0.0', 9090, prom_app)  # prometheus metrics endpoint
        httpd.serve_forever()

        # while True:
        #     time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        # th.tl.stop()

    observer.join()
