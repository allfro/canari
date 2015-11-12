@echo off

IF EXIST %~dp0\..\python.exe (
    %~dp0\..\python.exe %~dp0\pysudo %*
) else (
    @python %~dp0\pysudo %*
)
