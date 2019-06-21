FROM python:3.7-slim
RUN mkdir /tickets
COPY pyticket /pyticket
COPY tests /tests
COPY requirements.txt /
#COPY docker-entrypoint.sh /
#RUN chmod +x /docker-entrypoint.sh
RUN pip3 install -r requirements.txt
#WORKDIR /pyticket
CMD ["python3", "-m", "pyticket"]

#CMD ["/usr/local/bin/python3",  "pyticket_"]
