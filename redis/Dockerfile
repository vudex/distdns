FROM redis:alpine
RUN apk add --no-cache bash
COPY health-check.sh /usr/local/bin/
EXPOSE 6379/tcp
STOPSIGNAL SIGTERM
