#!/bin/sh
set -eu
umask 077
install -d -m 0700 /logs/verifier
chmod 0700 /logs/verifier
exec python3 /tests/grade.py
