:: Создает виртуальное окружение Python .ENV
:: для версии Python, указанной в PYTHON_EXE.
:: Обновляет пакеты из файла requirements.txt

@echo off

:: !!! Для конкретной версии Python Указать путь к папке, если пусто - Python по-умолчанию
:: set PYTHON_EXE=C:\Users\User\AppData\Local\Programs\Python\Python38\

:: Меняем директорию на папку с исполняемым файлом
cd /d %~dp0

:: Создаем виртуальное окружение Python в поддиректории .venv
%PYTHON_EXE%python.exe -m venv .venv

:: Активируем виртуальное окружение
IF NOT EXIST .venv\Scripts\activate.bat (
	echo Не найдено виртуальное окружение
    exit /b 1
)
call .venv\Scripts\activate.bat

:: Проверяем, активирована ли виртуальная среда
set VENV_PATH=%VIRTUAL_ENV%
set CURRENT_DIR=%CD%
if x%VENV_PATH:%CURRENT_DIR%=x%VENV_PATH%==x (
	echo Виртуальная среда не активна
	goto :EOF
) 

:: Обновляем pip до последней версии
python -m pip install --upgrade pip
:: python -m pip install --upgrade pip setuptools

:: Устанавливаем зависимости из файла requirements.txt
pip install -r requirements.txt


:: Деактивируем виртуальное окружение после завершения работы
call deactivate


