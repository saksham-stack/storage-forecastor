@echo off
call .venv\Scripts\activate
python scripts\generate_synthetic_data.py
python scripts\visualize_data.py
python scripts\train_baseline.py
