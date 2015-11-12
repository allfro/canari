@echo off

IF EXIST %~dp0\..\python.exe (
    %~dp0\..\python.exe %~dp0\canari %*
) else (
    @python %~dp0\canari %*
)
