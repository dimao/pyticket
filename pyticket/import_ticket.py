import logging

from zeep import Client


class ImportTicket:
    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)

    def __init__(self, wsdl, transport, settings):
        self.wsdl = wsdl
        self.transport = transport
        self.settings = settings

        try:
            self.client = Client(wsdl, transport=transport, settings=settings)
            self.logger.info(f'Current version: {self.client.service.GetCurrentVersion()}')
        except ConnectionError:
            self.logger.critical(f'Can\'t connect to {self.wsdl}')

    def get_client(self):
        return self.client

    def import_ticket(self, event_code, session_start, session_end, event_name, barcode_):
        import_ticket_result = self.client.service.ImportTicket(eventCode=int(event_code), areaCode=1, placeCode=1,
                                                                barcode=barcode_.rstrip(),
                                                                # strip \n at the end of line
                                                                row='1', seat='1')
        self.client.service.UpdateEventSession(eventCode=int(event_code), sessionCode=int(event_code),
                                               sessionStart=session_start,
                                               sessionEnd=session_end, eventName=event_name)
        self.client.service.ActivateTicket(barcode_.rstrip(), eventCode=int(event_code))
        return self.logger.info(import_ticket_result)
