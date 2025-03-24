@echo off
echo %cd%
pause
for /R %%G in (*.py *.cu *.c *.cpp *.h *.txt *.md *.mk) do dos2unix "%%G"
pause