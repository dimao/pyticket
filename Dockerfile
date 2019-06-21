FROM python:3.7-slim
RUN mkdir /tickets
COPY pyticket /pyticket
COPY tests /tests
COPY requirements.txt /
RUN pip3 install -r requirements.txt
CMD ["python3", "-m", "pyticket"]