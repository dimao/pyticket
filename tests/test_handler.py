import json

import arrow
from zeep import Transport, Settings

from pyticket import handler
from pyticket import import_ticket

with open('config.json', 'r') as f:
    config = json.load(f)


def test_scrape():
    html_string = handler.Scrape.scrape(config['site']['url'])
    next_game_date_string = html_string[0].strip('<p>\t')
    next_game_datetime = arrow.get(next_game_date_string, 'DD MMMM YYYY, HH:mm', locale='ru')
    assert type(next_game_datetime) is arrow.arrow.Arrow


def test_conn():
    wsdl = config['wsdl']['url']
    transport = Transport(timeout=10)
    settings = Settings(strict=False)  # because of invalid xml response when calling UpdateEventSession
    it = import_ticket.ImportTicket(wsdl, transport, settings)
    assert it.client.service.GetCurrentVersion() == '1.0.1.0'
