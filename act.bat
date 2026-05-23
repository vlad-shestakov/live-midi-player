@echo off

:: Меняем директорию на папку с исполняемым файлом
cd /d %~dp0

:: Активируем виртуальное окружение
call .venv\Scripts\activate.bat

:: Проверяем, активирована ли виртуальная среда
set VENV_PATH=%VIRTUAL_ENV%
set CURRENT_DIR=%CD%
if x%VENV_PATH:%CURRENT_DIR%=x%VENV_PATH%==x (
	echo Активная виртуальная среда не активна
	goto :EOF
) 