@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

if "%~1"=="" goto menu
if /I "%~1"=="show-config" goto cmd_show_config
if /I "%~1"=="list-ports" goto cmd_list_ports
if /I "%~1"=="set" goto cmd_set
if /I "%~1"=="run" goto cmd_run

goto usage

:cmd_show_config
"%PYTHON_EXE%" main.py --show-config
goto end

:cmd_list_ports
"%PYTHON_EXE%" main.py --list-ports
goto end

:cmd_set
"%PYTHON_EXE%" main.py --set-config %2 %3 %4 %5 %6 %7 %8 %9
goto end

:cmd_run
"%PYTHON_EXE%" main.py %2 %3 %4 %5 %6 %7 %8 %9
goto end

:menu
cls
echo ==========================================
echo     MIDI Port Configurator (interactive)
echo ==========================================
echo.
echo  1. Show saved config
echo  2. List current MIDI ports
echo  3. Set input port
echo  4. Set output port
echo  5. Set input and output ports
echo  6. Run player (main.py)
echo  0. Exit
echo.
set /p MENU_CHOICE=Select action: 

if "%MENU_CHOICE%"=="1" goto menu_show_config
if "%MENU_CHOICE%"=="2" goto menu_list_ports
if "%MENU_CHOICE%"=="3" goto menu_set_input
if "%MENU_CHOICE%"=="4" goto menu_set_output
if "%MENU_CHOICE%"=="5" goto menu_set_both
if "%MENU_CHOICE%"=="6" goto menu_run
if "%MENU_CHOICE%"=="0" goto end

echo Invalid option.
pause
goto menu

:menu_show_config
"%PYTHON_EXE%" main.py --show-config
echo.
pause
goto menu

:menu_list_ports
"%PYTHON_EXE%" main.py --list-ports
echo.
pause
goto menu

:menu_set_input
echo Enter input port name exactly as shown in list:
set /p INPUT_NAME=Input port: 
"%PYTHON_EXE%" main.py --set-config --input-port "%INPUT_NAME%"
echo.
pause
goto menu

:menu_set_output
echo Enter output port name exactly as shown in list:
set /p OUTPUT_NAME=Output port: 
"%PYTHON_EXE%" main.py --set-config --output-port "%OUTPUT_NAME%"
echo.
pause
goto menu

:menu_set_both
echo Enter input port name exactly as shown in list:
set /p INPUT_NAME=Input port: 
echo Enter output port name exactly as shown in list:
set /p OUTPUT_NAME=Output port: 
"%PYTHON_EXE%" main.py --set-config --input-port "%INPUT_NAME%" --output-port "%OUTPUT_NAME%"
echo.
pause
goto menu

:menu_run
echo Starting MIDI player with current config...
"%PYTHON_EXE%" main.py
echo.
pause
goto menu

:usage
echo Usage:
echo   configure_ports.bat
echo   configure_ports.bat show-config
echo   configure_ports.bat list-ports
echo   configure_ports.bat set --input-port "INPUT_NAME" --output-port "OUTPUT_NAME"
echo   configure_ports.bat run [main.py arguments]
echo.
echo Examples:
echo   configure_ports.bat set --input-port "LKMK3 MIDI 0"
echo   configure_ports.bat set --output-port "Microsoft GS Wavetable Synth 0"
echo   configure_ports.bat run --engine midi-out

:end
endlocal
