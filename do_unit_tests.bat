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

set COLOR_GREEN=0a
set COLOR_READ=04
set COLOR_WHITE = 0f
set FINAL_COLOR=%COLOR_GREEN%
color %COLOR_WHITE%

REM doing unit tests without invoking weird error
echo You may need to activate your virtual environment before invoking these.
echo Running: python -m unittest discover %VERBOSE_FLAG% tests\gvas_core
python -m unittest discover %VERBOSE_FLAG%  tests\gvas_core
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
echo Running: python -m unittest %VERBOSE_FLAG%  tests\test_gvas_examples.py
python -m unittest %VERBOSE_FLAG%  tests\test_gvas_examples.py
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%

color %FINAL_COLOR%
