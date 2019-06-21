FROM python:3.7-slim
RUN mkdir /pyticket /tickets
COPY pyticket /pyticket
COPY requirements.txt /
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
RUN pip3 install -r requirements.txt
#WORKDIR /pyticket
CMD ["/docker-entrypoint.sh"]

#CMD ["/usr/local/bin/python3",  "pyticket_"]
