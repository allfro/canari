@echo off

IF EXIST %~dp0\..\python.exe (
    %~dp0\..\python.exe %~dp0\dispatcher %*
) else (
    @python %~dp0\dispatcher %*
)
