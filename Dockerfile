FROM python:3.7-slim
ENV WSDL_URL=$WSDL_URL
ENV MON_FOLDER=$MON_FOLDER
ENV PROM_PORT=$PROM_PORT
ENV HOST_NAME=$HOST_NAME
ENV PORT=$PORT
RUN mkdir /tickets
COPY pyticket /pyticket
COPY tests /tests
COPY requirements.txt /
RUN pip3 install -r requirements.txt
CMD ["python3", "-m", "pyticket"]