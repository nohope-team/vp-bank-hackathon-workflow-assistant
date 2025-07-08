#!/bin/sh
set -x 

# load environment variables
source .env

# run server
python src/server.py
