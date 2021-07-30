#!/bin/sh

rc-service crond start

exec "$@"
