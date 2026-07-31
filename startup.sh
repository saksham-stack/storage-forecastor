#!/usr/bin/env bash
python -m streamlit run dashboard/app.py \
  --server.port ${PORT:-8000} \
  --server.address 0.0.0.0 \
  --server.headless true