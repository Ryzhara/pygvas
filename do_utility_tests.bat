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
set RESOURCE_DIR=resources\test

echo Cleaning up temporary files that might be lying around
echo.
if exist %TEST_GVAS% del %TEST_GVAS%
if exist %TEST_JSON% del %TEST_JSON%


echo ===== Testing a BIN file with hints =====
set TESTFILE=features_01
python pygvas/detect_gvas_format.py %RESOURCE_DIR%\%TESTFILE%.bin
python pygvas/gvas2json.py %RESOURCE_DIR%\%TESTFILE%.bin %TEST_JSON% --hints=%RESOURCE_DIR%\%TESTFILE%.hints.json
fc /A /B %TEST_JSON% %RESOURCE_DIR%\%TESTFILE%.bin.json
python pygvas/json2gvas.py %TEST_JSON% %TEST_GVAS%
fc /A /B %TEST_GVAS% %RESOURCE_DIR%\%TESTFILE%.bin

echo ===== Testing a file without hints =====
set TESTFILE=component8
python pygvas/detect_gvas_format.py %RESOURCE_DIR%\%TESTFILE%.sav
python pygvas/gvas2json.py %RESOURCE_DIR%\%TESTFILE%.sav %TEST_JSON%
fc /A /B %TEST_JSON% %RESOURCE_DIR%\%TESTFILE%.sav.json
python pygvas/json2gvas.py %TEST_JSON% %TEST_GVAS%
fc /A /B %TEST_GVAS% %RESOURCE_DIR%\%TESTFILE%.sav

echo ===== Testing a Palworld compresseed file without hints =====
set TESTFILE=palworld_zlib
python pygvas/detect_gvas_format.py %RESOURCE_DIR%\%TESTFILE%.sav
python pygvas/gvas2json.py %RESOURCE_DIR%\%TESTFILE%.sav %TEST_JSON%
fc /A /B %TEST_JSON% %RESOURCE_DIR%\%TESTFILE%.sav.json
python pygvas/json2gvas.py %TEST_JSON% %TEST_GVAS%
fc /A /B %TEST_GVAS% %RESOURCE_DIR%\%TESTFILE%.sav

echo Cleaning up temporary files
if exist %TEST_GVAS% del %TEST_GVAS%
if exist %TEST_JSON% del %TEST_JSON%