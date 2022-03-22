#!/bin/bash
uwsgi --ini uwsgi.ini &
nginx -g "daemon off;"
