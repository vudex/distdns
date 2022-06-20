#!/bin/sh
if nc -zv -w30 $HOSTNAME 8082 &>/dev/null; then
        echo "[+] health-cheak ok"
else
        echo "[-] powergslb dont listen 8082 port"
        exit 1
fi
