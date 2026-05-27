@echo off
chcp 65001 > nul
title Установка системы Бюджет-Культура Сочи

cd /d "%~dp0"

echo.
echo  ================================================================
echo   Установка системы "Бюджет-Культура Сочи"
echo  ================================================================
echo.

:: Проверяем наличие Python
python --version > nul 2>&1
if errorlevel 1 (
    echo  ОШИБКА: Python не найден на вашем компьютере.
    echo.
    echo  Пожалуйста, установите Python 3.11 или новее:
    echo  1. Откройте браузер и перейдите на сайт: https://www.python.org/downloads/
    echo  2. Нажмите большую кнопку "Download Python"
    echo  3. При установке ОБЯЗАТЕЛЬНО поставьте галочку "Add Python to PATH"
    echo  4. После установки запустите этот файл снова
    echo.
    pause
    exit /b 1
)

echo  Python найден. Продолжаем установку...
echo.

:: Создаём виртуальную среду
echo  [Шаг 1 из 5] Подготовка рабочей среды...
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo  ОШИБКА при создании рабочей среды. Попробуйте переустановить Python.
        pause
        exit /b 1
    )
)
echo  Готово.
echo.

:: Активируем и устанавливаем пакеты
echo  [Шаг 2 из 5] Установка необходимых компонентов (может занять 2-5 минут)...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q --no-warn-script-location
if errorlevel 1 (
    echo  ОШИБКА при установке компонентов. Проверьте подключение к интернету.
    pause
    exit /b 1
)
echo  Готово.
echo.

:: Создаём базу данных
echo  [Шаг 3 из 5] Создание базы данных...
python manage.py migrate --run-syncdb -v 0
if errorlevel 1 (
    echo  ОШИБКА при создании базы данных.
    pause
    exit /b 1
)
echo  Готово.
echo.

:: Загружаем классификаторы
echo  [Шаг 4 из 5] Загрузка бюджетных классификаторов...
python manage.py seed_classifiers
if errorlevel 1 (
    echo  ОШИБКА при загрузке классификаторов.
    pause
    exit /b 1
)
echo  Готово.
echo.

:: Создаём демо-данные
echo  [Шаг 5 из 5] Создание демонстрационных данных...
python manage.py create_demo_data
if errorlevel 1 (
    echo  ОШИБКА при создании демонстрационных данных.
    pause
    exit /b 1
)

echo.
echo  ================================================================
echo   Установка успешно завершена!
echo.
echo   Для запуска системы дважды нажмите на файл:
echo   ЗАПУСК.bat
echo  ================================================================
echo.
pause
