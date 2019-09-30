FROM python:3.6.6-stretch

COPY . /usr/src/package

RUN set -x \
    && cd /usr/src/package \
    && export FLASK_ENV=development \
    && mkdir -p /usr/local/var/log \
    && mkdir -p /storage/kycfile/whitelisted \
    && mkdir -p /storage/kycfile/consider \
    && mkdir -p /storage/kycfile/onboarded \
    && cp docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
