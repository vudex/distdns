#!/bin/sh
if nc -zv -w30 $HOSTNAME 53 &>/dev/null; then
        echo "[+] health-check ok"
else
        echo "[-] dnsdist dont listen 53 port"
        exit 1
fi
