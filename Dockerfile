FROM python:3.7-stretch
RUN mkdir /pyticket /tickets
COPY ./pyticket /pyticket
COPY requirements.txt /
RUN pip3 install -r requirements.txt
WORKDIR /
CMD ["/usr/local/bin/python3",  "pyticket"]
