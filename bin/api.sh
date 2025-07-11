#!/bin/sh
set -x 

# load environment variables
source .env

# run server
python3 src/server.py
