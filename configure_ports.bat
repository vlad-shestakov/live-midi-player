@echo off
setlocal EnableDelayedExpansion

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
echo   Настройка MIDI-портов (интерактивно)
echo ==========================================
echo.
echo  1. Показать сохраненную конфигурацию
echo  2. Показать текущие MIDI-порты
echo  3. Установить входной порт
echo  4. Установить выходной порт
echo  5. Установить входной и выходной порты
echo  6. Запустить плеер (main.py)
echo  0. Выход
echo.
set /p MENU_CHOICE=Выберите действие: 

if "%MENU_CHOICE%"=="1" goto menu_show_config
if "%MENU_CHOICE%"=="2" goto menu_list_ports
if "%MENU_CHOICE%"=="3" goto menu_set_input
if "%MENU_CHOICE%"=="4" goto menu_set_output
if "%MENU_CHOICE%"=="5" goto menu_set_both
if "%MENU_CHOICE%"=="6" goto menu_run
if "%MENU_CHOICE%"=="0" goto end

echo Неверный пункт меню.
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
call :select_port_by_number "input" INPUT_NAME
if errorlevel 1 goto menu
"%PYTHON_EXE%" main.py --set-config --input-port "!INPUT_NAME!"
echo.
pause
goto menu

:menu_set_output
call :select_port_by_number "output" OUTPUT_NAME
if errorlevel 1 goto menu
"%PYTHON_EXE%" main.py --set-config --output-port "!OUTPUT_NAME!"
echo.
pause
goto menu

:menu_set_both
echo Введите имя входного порта точно как в списке:
set /p INPUT_NAME=Входной порт: 
echo Введите имя выходного порта точно как в списке:
set /p OUTPUT_NAME=Выходной порт: 
"%PYTHON_EXE%" main.py --set-config --input-port "%INPUT_NAME%" --output-port "%OUTPUT_NAME%"
echo.
pause
goto menu

:menu_run
echo Запуск MIDI-плеера с текущей конфигурацией...
"%PYTHON_EXE%" main.py
echo.
pause
goto menu

:usage
echo Использование:
echo   configure_ports.bat
echo   configure_ports.bat show-config
echo   configure_ports.bat list-ports
echo   configure_ports.bat set --input-port "ИМЯ_ВХОДА" --output-port "ИМЯ_ВЫХОДА"
echo   configure_ports.bat run [аргументы main.py]
echo.
echo Примеры:
echo   configure_ports.bat set --input-port "LKMK3 MIDI 0"
echo   configure_ports.bat set --output-port "Microsoft GS Wavetable Synth 0"
echo   configure_ports.bat run --engine midi-out

goto end

:select_port_by_number
set "PORT_KIND=%~1"
set "PORT_COUNT=0"
for /f "tokens=1 delims==" %%V in ('set PORT_ 2^>nul') do set "%%V="

if /I "%PORT_KIND%"=="input" (
    set "PORT_LABEL=входных"
) else (
    set "PORT_LABEL=выходных"
)

for /f "usebackq delims=" %%L in (`"%PYTHON_EXE%" main.py --list-ports`) do (
    set "LINE=%%L"

    if "!LINE!"=="Входные MIDI-порты:" set "SECTION=input"
    if "!LINE!"=="Выходные MIDI-порты:" set "SECTION=output"

    if defined SECTION (
        echo !LINE! | findstr /R "^[ ]*[0-9][0-9]*\..*" >nul
        if not errorlevel 1 (
            set "ENTRY=!LINE:*.=!"
            if "!ENTRY:~0,1!"==" " set "ENTRY=!ENTRY:~1!"
            if /I "!SECTION!"=="!PORT_KIND!" (
                set /a PORT_COUNT+=1
                set "PORT_!PORT_COUNT!=!ENTRY!"
            )
        )
    )
)

if !PORT_COUNT! LEQ 0 (
    echo Не найдено !PORT_LABEL! MIDI-портов.
    exit /b 1
)

echo Доступные !PORT_LABEL! MIDI-порты:
for /L %%I in (1,1,!PORT_COUNT!) do echo   %%I. !PORT_%%I!
echo.

:select_port_retry
set "PORT_INDEX="
set /p PORT_INDEX=Выберите порт по номеру: 

if not defined PORT_INDEX (
    echo Введите число от 1 до !PORT_COUNT!.
    goto select_port_retry
)

echo(!PORT_INDEX! | findstr /R "^[1-9][0-9]*$" >nul
if errorlevel 1 (
    echo Введите число от 1 до !PORT_COUNT!.
    goto select_port_retry
)

if !PORT_INDEX! GTR !PORT_COUNT! (
    echo Номер вне диапазона. Доступно: 1..!PORT_COUNT!.
    goto select_port_retry
)

for %%I in (!PORT_INDEX!) do set "SELECTED_PORT=!PORT_%%I!"
set "%~2=!SELECTED_PORT!"
exit /b 0

:end
endlocal
