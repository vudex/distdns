FROM alpine AS builder

RUN apk --update upgrade \
        && apk add \
                ca-certificates \
                curl \
                jq \
        && apk add --virtual .build-depends \
                file \
                gnupg \
                g++ \
                make \
                boost-dev \
                libsodium-dev \
                lua-dev \
                net-snmp-dev \
                protobuf-dev \
                libedit-dev \
                re2-dev

#               libressl-dev \

ENV DNSDIST_VERSION=1.4.0

RUN  [ -n "$DNSDIST_VERSION" ] || { curl -sSL 'https://api.github.com/repos/PowerDNS/pdns/tags?per_page=100&page={1,2}' | jq -rs '[.[][]]|map(select(has("name")))|map(select(.name|contains("dnsdist-")))|map(.version=(.name|ltrimstr("dnsdist-")))|map(select(true != (.version|contains("-"))))|max_by(.version)|"DNSDIST_VERSION="+.version' > /tmp/latest-dnsdist-tag.sh && . /tmp/latest-dnsdist-tag.sh; }  \
        && mkdir -v -m 0700 -p /root/.gnupg \
        && curl -RL -O 'https://dnsdist.org/_static/dnsdist-keyblock.asc' \
        && gpg2 --no-options --verbose --keyid-format 0xlong --keyserver-options auto-key-retrieve=true --import *.asc \
        && curl -RL -O "https://downloads.powerdns.com/releases/dnsdist-${DNSDIST_VERSION}.tar.bz2{.asc,.sig,}" \
        && gpg2 --no-options --verbose --keyid-format 0xlong --keyserver-options auto-key-retrieve=true --verify *.sig \
        && rm -rf /root/.gnupg *.asc *.sig \
        && tar -xpf "dnsdist-${DNSDIST_VERSION}.tar.bz2" \
        && rm -f "dnsdist-${DNSDIST_VERSION}.tar.bz2" 

RUN cd "dnsdist-${DNSDIST_VERSION}" \
        && ./configure --sysconfdir=/etc/dnsdist --mandir=/usr/share/man \
                --enable-dnscrypt \
                --enable-dns-over-tls \
                --enable-libsodium \
                --enable-re2 \
                --with-net-snmp \
        && make -j$(nproc) \
        && make install-strip \
        && apk del --purge .build-depends && rm -rf /var/cache/apk/*

FROM alpine

RUN apk --update upgrade \
        && apk add \
                ca-certificates \
                curl \
                less \
                #man \
		mandoc \
                libressl \
                libsodium \
                lua \
                net-snmp \
                protobuf \
                libedit \
                re2 \
        && rm -rf /var/cache/apk/*

ENV PAGER less

RUN addgroup -S dnsdist && adduser -S -D -G dnsdist dnsdist

COPY --from=builder /usr/local/bin /usr/local/bin/
COPY --from=builder /usr/share/man/man1 /usr/share/man/man1/
COPY health-check.sh /usr/local/bin/

EXPOSE 53/tcp 53/udp 8082/tcp
ENTRYPOINT ["/usr/local/bin/dnsdist"]
STOPSIGNAL SIGTERM
