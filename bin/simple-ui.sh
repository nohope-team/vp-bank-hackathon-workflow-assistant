#!/bin/sh
set -x 

# load environment variables
source .env

# run server
streamlit run src/streamlit_app.py
