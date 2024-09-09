#!/bin/bash

# Activate the virtual environment
source /home/binge+/streamlit/venv/bin/activate

# Define the Streamlit application file (e.g., app.py)
APP_FILE="app.py"

# Start the Streamlit application in the background
nohup streamlit run $APP_FILE --server.address 0.0.0.0 --server.port 8501 > streamlit.log 2>&1 &
