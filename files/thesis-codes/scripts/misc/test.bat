@echo off
SET CURRENTDIR=%cd%
echo salam %~dp0
set SCR1=script = \"%~dp0 \\ allpaths.py\"
c:\Python27\python.exe -i -c "%SCR1%"
echo %SCR1%
