@echo off
:: Запускает автотесты проекта.
:: Используйте для локальной проверки перед запуском MIDI-режима.

:: Меняем директорию на папку со скриптом
cd /d %~dp0

:: Активируем виртуальное окружение
IF not EXIST .venv\Scripts\activate.bat (
    echo Не найдено виртуальное окружение
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

:: Проверяем, активирована ли виртуальная среда
if not defined VIRTUAL_ENV (
    echo Виртуальная среда не активна
    pause
    exit /b 1
)

echo Запуск автотестов...
python -m unittest discover -s tests -p "test_*.py"
set "TEST_EXIT_CODE=%ERRORLEVEL%"

if "%TEST_EXIT_CODE%"=="0" goto tests_ok
echo Тесты завершились с ошибкой. Код %TEST_EXIT_CODE%.
pause
exit /b %TEST_EXIT_CODE%

:tests_ok
echo Тесты успешно пройдены.
pause
exit /b 0
