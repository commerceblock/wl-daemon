FROM python:3.6.6-stretch

COPY . /usr/src/package

RUN set -x \
    && cd /usr/src/package \
    && python3 setup.py build \
    && python3 setup.py install \
    && cp docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
