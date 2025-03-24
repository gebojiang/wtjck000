@echo off
chcp 65001
cls
set /p classname=请输入要删除的类名: 
echo 删除的类是: %classname%

cd Source

set "classh=%classname%.h"
set "classcpp=%classname%.cpp"


echo 删除的.h文件是: %classh%
echo 删除的.cpp文件是 : %classcpp%




del /s /q "%classcpp%" "%classh%" 2>nul



cd ..

echo 删除Binaries文件夹.

rd /s  /q  Binaries


setlocal enabledelayedexpansion
set "path_str="
for /f "delims=" %%i in ('dir /s /b *.uproject') do (
    set "path_str=!path_str!%%i"
)

echo 重新生成.uproject文件: %path_str%

D:/UE_4.27/Engine/Binaries/DotNET/UnrealBuildTool.exe  -projectfiles -project=%path_str% -game -engine -progress


pause