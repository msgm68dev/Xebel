@echo off


SET CURRENTDIR="%cd%"
SET FILENAME="allpaths.py"
Rem SET MYCODE=%CURRENTDIR%%FILENAME% 
echo MyCode: !MYCODE! 
Rem myvar=!myvar! %%i
SET s=%CURRENTDIR%%FILENAME% 
echo khkhkh %CURRENTDIR FILENAME%
Rem This program just displays Hello World
Rem c:\Python27\python.exe -i -c "exec(open('e:/Mostafa/PHD/THESIS/TEZ/Pythons/AllPaths/allPaths/allpaths.py').read())"
Rem c:\Python27\python.exe -i -c "scriptdir = \"%CURRENTDIR%\"" -c "script = scriptdir + \"allpaths.py\"" -c "print script"
c:\Python27\python.exe -i -c "scriptdir = \"%CURRENTDIR%\" & a=2222"
Rem c:\Python27\python.exe -i -c "exec(open('%MYCODE%).read())"
pause