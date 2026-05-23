@echo off
:: Запускает автотесты проекта.
:: Используйте для локальной проверки перед запуском MIDI-режима.

::все тесты
::   run_tests.bat 
::только один тест 
::   run_tests.bat tests/test_favorites_logic.py
::   run_tests.bat tests/test_program_names.py
::только один тест метода
::   run_tests.bat tests/test_program_names.py::test_gm_program_name_hit


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

set "TEST_TARGET=%~1"
if not defined TEST_TARGET (
    echo Запуск автотестов... mode=full-suite
    python -m unittest discover -s tests -p "test_*.py"
) else (
    echo Запуск автотестов... mode=targeted target=%TEST_TARGET%
    python -m unittest "%TEST_TARGET%"
)
set "TEST_EXIT_CODE=%ERRORLEVEL%"

if "%TEST_EXIT_CODE%"=="0" goto tests_ok
echo Тесты завершились с ошибкой. Код %TEST_EXIT_CODE%.
pause
exit /b %TEST_EXIT_CODE%

:tests_ok
echo Тесты успешно пройдены.
pause
exit /b 0
