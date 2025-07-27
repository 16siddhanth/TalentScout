#!/bin/bash
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
