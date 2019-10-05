FROM python:3.6.6-stretch

COPY . /usr/src/package

RUN set -x \
    && cd /usr/src/package \
    && python3 setup.py build \
    && python3 setup.py install \
    && pip3 install -r requirements.txt 

COPY docker-entrypoint.sh /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
