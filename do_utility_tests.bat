@echo off
setlocal enabledelayedexpansion


rem test each utility
echo You may need to activate your virtual environment before invoking these.
echo.

set PACKAGE_NAME=pygvas

echo Checking if %PACKAGE_NAME% is installed...
pip show %PACKAGE_NAME% >nul 2>&1

if %ERRORLEVEL%==0 (
    echo %PACKAGE_NAME% is already installed.
) else (
    echo %PACKAGE_NAME% is NOT installed. Doing 'pip install -e .'
    pip install -e .
)

set TEST_GVAS=utility_test_result__.gvas
set TEST_JSON=utility_test_result__.json
set TEST_HINTS_JSON=utility_test_hints_result__.json
set RESOURCE_DIR=resources\test

echo Cleaning up temporary files that might be lying around
echo.
if exist %TEST_GVAS% del %TEST_GVAS%
if exist %TEST_JSON% del %TEST_JSON%
if exist %TEST_HINTS_JSON% del %TEST_JSON%

set COLOR_GREEN=0a
set COLOR_READ=04
set COLOR_WHITE = 0f
set FINAL_COLOR=%COLOR_GREEN%
color %COLOR_WHITE%

echo ===== Testing a BIN file with hints =====
set TESTFILE=features_01
python pygvas/detect_gvas_format.py %RESOURCE_DIR%\%TESTFILE%.bin
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
python pygvas/gvas2json.py %RESOURCE_DIR%\%TESTFILE%.bin %TEST_JSON% --hints=%RESOURCE_DIR%\%TESTFILE%.hints.json
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
fc /A /B %TEST_JSON% %RESOURCE_DIR%\%TESTFILE%.bin.json
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
python pygvas/json2gvas.py %TEST_JSON% %TEST_GVAS%
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
fc /A /B %TEST_GVAS% %RESOURCE_DIR%\%TESTFILE%.bin
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%

echo ===== Testing a file without hints but CREATE one =====
set TESTFILE=component8
python pygvas/detect_gvas_format.py %RESOURCE_DIR%\%TESTFILE%.sav
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
python pygvas/gvas2json.py %RESOURCE_DIR%\%TESTFILE%.sav %TEST_JSON% --hints=%RESOURCE_DIR%\%TEST_HINTS_JSON%.hints.json --update_hints
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
if not exist %RESOURCE_DIR%\%TEST_HINTS_JSON%.hints.json echo Failed to create hints file!
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
if exist %RESOURCE_DIR%\%TEST_HINTS_JSON%.hints.json echo Hints file successfully created.
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
fc /A /B %TEST_JSON% %RESOURCE_DIR%\%TESTFILE%.sav.json
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
python pygvas/json2gvas.py %TEST_JSON% %TEST_GVAS%
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
fc /A /B %TEST_GVAS% %RESOURCE_DIR%\%TESTFILE%.sav
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%

echo ===== Testing a Palworld compresseed file without hints =====
set TESTFILE=palworld_zlib
python pygvas/detect_gvas_format.py %RESOURCE_DIR%\%TESTFILE%.sav
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
python pygvas/gvas2json.py %RESOURCE_DIR%\%TESTFILE%.sav %TEST_JSON%
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
fc /A /B %TEST_JSON% %RESOURCE_DIR%\%TESTFILE%.sav.json
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
python pygvas/json2gvas.py %TEST_JSON% %TEST_GVAS%
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%
fc /A /B %TEST_GVAS% %RESOURCE_DIR%\%TESTFILE%.sav
if not %ERRORLEVEL%==0 set FINAL_COLOR=%COLOR_RED%

color %FINAL_COLOR%

echo Cleaning up temporary files
if exist %TEST_GVAS% del %TEST_GVAS%
if exist %TEST_JSON% del %TEST_JSON%
if exist %TEST_HINTS_JSON% del %TEST_JSON%
