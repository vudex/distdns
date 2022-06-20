FROM alpine AS builder

RUN apk --update upgrade \
        && apk add \
                ca-certificates \
                curl \
                jq
RUN apk add --virtual .build-depends \
                file \
                gnupg \
                g++ \
                make \
                boost-dev \
                libressl-dev \
                libsodium-dev \
		lua-dev \
                net-snmp-dev \
                protobuf-dev \
                postgresql-dev \
		curl-dev \
		libcurl \
                yaml-cpp-dev

ENV AUTH_VERSION=4.3.0

RUN [ -n "$AUTH_VERSION" ] || { curl -sSL 'https://api.github.com/repos/PowerDNS/pdns/tags?per_page=100&page={1,2}' | jq -rs '[.[][]]|map(select(has("name")))|map(select(.name|contains("auth-")))|map(.version=(.name|ltrimstr("auth-")))|map(select(true != (.version|contains("-"))))|max_by(.version)|"AUTH_VERSION="+.version' > /tmp/latest-auth-tag.sh && . /tmp/latest-auth-tag.sh; } \
        && mkdir -v -m 0700 -p /root/.gnupg \
        && curl -RL -O 'https://www.powerdns.com/powerdns-keyblock.asc' \
        && gpg2 --no-options --verbose --keyid-format 0xlong --keyserver-options auto-key-retrieve=true --import *.asc \
        && curl -RL -O "https://downloads.powerdns.com/releases/pdns-${AUTH_VERSION}.tar.bz2{.asc,.sig,}" \
        && gpg2 --no-options --verbose --keyid-format 0xlong --keyserver-options auto-key-retrieve=true --verify *.sig \
        && rm -rf /root/.gnupg *.asc *.sig \
        && tar -xpf "pdns-${AUTH_VERSION}.tar.bz2" \
        && rm -f "pdns-${AUTH_VERSION}.tar.bz2"

RUN cd "pdns-${AUTH_VERSION}" \
        && ./configure --sysconfdir=/etc/pdns --mandir=/usr/share/man \
            --enable-libsodium --enable-tools \
            --with-modules='pipe' \
            --with-dynmodules='lua2 random remote gpgsql' \
        && make -j$(nproc) \
        && make install-strip \
        && apk del --purge .build-depends && rm -rf /var/cache/apk/*

#FROM python:2.7-alpine3.12
FROM python2-custom

RUN apk --update upgrade \
        && apk add \
                ca-certificates \
                curl \
                less \
                #man \
                mandoc \
		boost \
                boost-program_options \
                libressl \
                libsodium \
                lua \
                net-snmp \
                protobuf \
                libpq \
                geoip \
                yaml-cpp

RUN apk add --virtual .build-deps \
                gcc \
                musl-dev \
                postgresql-dev \
        && python -m pip install --no-cache-dir \
                redis \
                pyping \
                netaddr \
                subprocess32 \
                psycopg2-binary \
        && apk --purge del .build-deps \
        && rm -rf /var/cache/apk/*

ENV PAGER less

RUN addgroup -S pdns && adduser -S -D -G pdns pdns

COPY --from=builder /usr/local/bin /usr/local/bin/
COPY --from=builder /usr/local/sbin /usr/local/sbin/
COPY --from=builder /usr/local/lib/pdns /usr/local/lib/pdns
COPY --from=builder /usr/share/man/man1 /usr/share/man/man1/
COPY --from=builder /usr/local/share/doc/pdns /usr/local/share/doc/pdns
COPY --from=builder /etc/pdns /etc/pdns/

EXPOSE 5300/tcp 5300/udp 8081/tcp
ENTRYPOINT ["/usr/local/sbin/pdns_server"]
STOPSIGNAL SIGTERM
