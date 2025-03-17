# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Set PYTHONPATH and run the application
$env:PYTHONPATH = ".;$env:PYTHONPATH"
python src/gui/zip_input_app.py

# Deactivate virtual environment when done
deactivate 