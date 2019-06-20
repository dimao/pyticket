FROM python:3.7-stretch
ENV scrape_interval=${scrape_interval}
RUN apt-get clean && apt-get update && apt-get install -y locales curl
RUN echo 'ru_RU.UTF-8 UTF-8' > /etc/locale.gen && \
    locale-gen
ENV LC_ALL=ru_RU.UTF-8
#ENV LANG ru_RU.UTF-8
#ENV LC_ALL ru_RU.UTF-8
#ENV LC_TIME ru_RU.UTF-8
RUN mkdir /pyticket /tickets
COPY ./pyticket /pyticket
COPY requirements.txt /
COPY docker-entrypoint.sh /
RUN pip3 install -r requirements.txt
RUN chmod +x /docker-entrypoint.sh
WORKDIR /
CMD ["bash"]
#CMD ["/docker-entrypoint.sh"]


#CMD ["/usr/local/bin/python3 pyticket /tickets"]
