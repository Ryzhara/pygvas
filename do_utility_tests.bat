@echo off
setlocal enabledelayedexpansion


rem test each utility
echo You may need to activate your virtual environment before invoking these.
echo.
set TEST_GVAS=test_result.gvas
set TEST_JSON=test_result.json

echo Cleaning up temporary files that might be lying around
echo.
if exist %TEST_GVAS% del %TEST_GVAS%
if exist %TEST_JSON% del %TEST_JSON%

echo ===== Testing a BIN file with hints =====
set TESTFILE=features_01
python detect_gvas_format.py resources\test\%TESTFILE%.bin
python gvas2json.py resources\test\%TESTFILE%.bin test_result.json --hints=resources\test\%TESTFILE%.hints.json
fc test_result.json resources\test\%TESTFILE%.bin.json
python json2gvas.py test_result.json test_result.gvas
fc /B test_result.gvas resources\test\%TESTFILE%.bin

echo ===== Testing a file without hints =====
set TESTFILE=component8
python detect_gvas_format.py resources\test\%TESTFILE%.sav
python gvas2json.py resources\test\%TESTFILE%.sav test_result.json
fc /B test_result.json resources\test\%TESTFILE%.sav.json
python json2gvas.py test_result.json test_result.gvas
fc /B test_result.gvas resources\test\%TESTFILE%.sav

echo ===== Testing a Palworld compresseed file without hints =====
set TESTFILE=palworld_zlib
python detect_gvas_format.py resources\test\%TESTFILE%.sav
python gvas2json.py resources\test\%TESTFILE%.sav test_result.json
fc /B test_result.json resources\test\%TESTFILE%.sav.json
python json2gvas.py test_result.json test_result.gvas
fc /B test_result.gvas resources\test\%TESTFILE%.sav

echo Cleaning up temporary files
if exist %TEST_GVAS% del %TEST_GVAS%
if exist %TEST_JSON% del %TEST_JSON%