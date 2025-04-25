@echo off
setlocal enabledelayedexpansion


rem test each utility
echo You may need to activate your virtual environment before invoking these.
echo.
set TEST_GVAS=utility_test_result__.gvas
set TEST_JSON=utility_test_result__.json

echo Cleaning up temporary files that might be lying around
echo.
if exist %TEST_GVAS% del %TEST_GVAS%
if exist %TEST_JSON% del %TEST_JSON%

echo ===== Testing a BIN file with hints =====
set TESTFILE=features_01
python detect_gvas_format.py resources\test\%TESTFILE%.bin
python gvas2json.py resources\test\%TESTFILE%.bin %TEST_JSON% --hints=resources\test\%TESTFILE%.hints.json
fc %TEST_JSON% resources\test\%TESTFILE%.bin.json
python json2gvas.py %TEST_JSON% %TEST_GVAS%
fc /B %TEST_GVAS% resources\test\%TESTFILE%.bin

echo ===== Testing a file without hints =====
set TESTFILE=component8
python detect_gvas_format.py resources\test\%TESTFILE%.sav
python gvas2json.py resources\test\%TESTFILE%.sav %TEST_JSON%
fc /B %TEST_JSON% resources\test\%TESTFILE%.sav.json
python json2gvas.py %TEST_JSON% %TEST_GVAS%
fc /B %TEST_GVAS% resources\test\%TESTFILE%.sav

echo ===== Testing a Palworld compresseed file without hints =====
set TESTFILE=palworld_zlib
python detect_gvas_format.py resources\test\%TESTFILE%.sav
python gvas2json.py resources\test\%TESTFILE%.sav %TEST_JSON%
fc /B %TEST_JSON% resources\test\%TESTFILE%.sav.json
python json2gvas.py %TEST_JSON% %TEST_GVAS%
fc /B %TEST_GVAS% resources\test\%TESTFILE%.sav

echo Cleaning up temporary files
if exist %TEST_GVAS% del %TEST_GVAS%
if exist %TEST_JSON% del %TEST_JSON%