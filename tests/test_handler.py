import os
from zeep import Transport, Settings
from pyticket import import_ticket


def test_conn():
    wsdl = os.environ.get('WSDL_URL')
    transport = Transport(timeout=10)
    settings = Settings(strict=False)  # because of invalid xml response when calling UpdateEventSession
    it = import_ticket.ImportTicket(wsdl, transport, settings)
    assert it.client.service.GetCurrentVersion() == '1.0.1.0'
