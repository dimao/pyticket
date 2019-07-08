import logging
import socket
import os
from gevent.pywsgi import WSGIServer

from prometheus_client import make_wsgi_app
from watchdog.observers import Observer

from pyticket.handler import TicketsHandler

if __name__ == '__main__':

    path = os.environ.get('MON_FOLDER')

    observer = Observer()
    tickets_handler = TicketsHandler()

    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    logger.info(f'Monitoring {path} directory')

    observer.schedule(tickets_handler, path=path, recursive=False)
    observer.start()

    metrics_app = make_wsgi_app()

    prom_port = int(os.environ.get('PROM_PORT'))
    fqdn = socket.getfqdn()

    def prom_app(environ, start_fn):

        if environ['PATH_INFO'] == '/metrics':
            return metrics_app(environ, start_fn)
        start_fn('200 OK', [])
        return [b'<a href="http://{}:{}/metrics">metrics<a>'.decode().format(
            fqdn, prom_port).encode()]  # decode bytes to string, interpolate variable and encode again


    try:
        logger.info(f"Prometheus endpoint on http://{fqdn}:{prom_port}/metrics")
        WSGIServer(('0.0.0.0', prom_port), prom_app, log=logger).serve_forever()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
