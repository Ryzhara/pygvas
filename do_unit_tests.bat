@echo off
setlocal enabledelayedexpansion

REM Default: no verbose flag
set VERBOSE_FLAG=

REM Parse arguments
:parse_args
if "%~1"=="" goto done_parse
if "%~1"=="-v" (
    set VERBOSE_FLAG=-v
) else (
    REM You can handle other args here if needed
)
shift
goto parse_args

:done_parse

REM doing unit tests without invoking weird error
echo You may need to activate your virtual environment before invoking these.
echo Running: python -m unittest discover %VERBOSE_FLAG% tests\gvas_core
python -m unittest discover %VERBOSE_FLAG%  tests\gvas_core
echo Running: python -m unittest %VERBOSE_FLAG%  tests\test_gvas_examples.py
python -m unittest %VERBOSE_FLAG%  tests\test_gvas_examples.py