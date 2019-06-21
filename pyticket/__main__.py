import json
import logging
import socket
from datetime import timedelta
from wsgiref.simple_server import make_server

from prometheus_client import make_wsgi_app
from timeloop import Timeloop
from watchdog.observers import Observer

from pyticket.handler import TicketsHandler

if __name__ == '__main__':

    with open('config.json', 'r') as f:
        config = json.load(f)
    path = config['game']['folder']

    observer = Observer()
    tickets_handler = TicketsHandler()
    tickets_handler.scrape()  # 1st scrape
    timeloop = Timeloop()

    scrape_interval = config['site']['scrape_interval']


    @timeloop.job(interval=timedelta(seconds=int(scrape_interval)))  # scraping with interval
    def timeloop_job():
        tickets_handler.scrape()


    timeloop.start()  # start timeloop thread
    logger = logging.getLogger('handler')
    logger.info(f'Monitoring {path} directory with {scrape_interval} seconds interval')

    observer.schedule(tickets_handler, path=path, recursive=False)
    observer.start()

    metrics_app = make_wsgi_app()


    def prom_app(environ, start_fn):
        fqdn = socket.getfqdn()
        if environ['PATH_INFO'] == '/metrics':
            return metrics_app(environ, start_fn)
        start_fn('200 OK', [])
        return [b'<a href="http://{}:9090/metrics">metrics<a>'.decode().format(
            fqdn).encode()]  # decode bytes to string, interpolate variable and encode again


    prom_port = config['prometheus']['port']

    try:
        httpd = make_server('0.0.0.0', prom_port, prom_app)  # prometheus metrics endpoint
        httpd.serve_forever()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
