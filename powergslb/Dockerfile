FROM python:2.7-slim-stretch
RUN apt update && apt install -y \
	gcc \
	musl-dev 

RUN python -m pip install --no-cache-dir \
		pyping \
		subprocess32 \
		psycopg2-binary \
		redis \
		netaddr \
	&& apt clean

ADD . /opt/powergslb
COPY health-check.sh /usr/local/bin/

EXPOSE 8080
STOPSIGNAL SIGTERM
