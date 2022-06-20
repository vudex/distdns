#!/bin/bash
set -eo pipefail

host="$(hostname -i || echo '127.0.0.1')"

if ping="$(redis-cli -h "$host" -a b66056f86915a24e27877ef6ab4d8c4b15652c9139b09abfa5844ec1231379c5 ping)" && [ "$ping" = 'PONG' ]; then
        exit 0
fi

exit 1
