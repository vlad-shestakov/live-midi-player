@echo off
:: Запускает сервер бота VladShestakovBot
:: После запуска можно пользоваться ботом.



:: Меняем директорию на папку с исполняемым файлом
cd /d %~dp0

:: Активируем виртуальное окружение
IF not EXIST .venv\Scripts\activate.bat (
	echo Не найдено виртуальное окружение
	exit /b 1
)

call .venv\Scripts\activate.bat

:: Проверяем, активирована ли виртуальная среда
set VENV_PATH=%VIRTUAL_ENV%
set CURRENT_DIR=%CD%
if x%VENV_PATH:%CURRENT_DIR%=x%VENV_PATH%==x (
	echo Виртуальная среда не активна
    	exit /b 1
) 

:: Запускаем сервер
python "main.py"
@REM python "main.py" --engine midi-out --verbose
@REM python "main.py" --list-ports