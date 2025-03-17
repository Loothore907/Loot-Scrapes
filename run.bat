@echo off
REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set PYTHONPATH and run the application
set PYTHONPATH=.;%PYTHONPATH%
python src/gui/zip_input_app.py

REM Deactivate virtual environment when done
deactivate 