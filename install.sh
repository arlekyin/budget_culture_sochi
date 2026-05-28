#!/bin/bash
cd "$(dirname "$0")"

echo ""
echo "================================================================"
echo "  Установка системы «Бюджет-Культура Сочи»"
echo "================================================================"
echo ""

# Проверяем Python
if ! command -v python3 &>/dev/null; then
    echo "ОШИБКА: Python 3 не найден."
    echo ""
    echo "Установите его с официального сайта:"
    echo "https://www.python.org/downloads/"
    echo ""
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

echo "Python найден: $(python3 --version)"
echo ""

# Виртуальная среда
echo "[Шаг 1 из 3] Подготовка рабочей среды..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "Готово."
echo ""

# Установка зависимостей
echo "[Шаг 2 из 3] Установка компонентов (2-5 минут)..."
pip install -r requirements.txt -q --no-warn-script-location
if [ $? -ne 0 ]; then
    echo "ОШИБКА при установке. Проверьте подключение к интернету."
    read -p "Нажмите Enter для выхода..."
    exit 1
fi
echo "Готово."
echo ""

# Проверяем наличие базы данных
echo "[Шаг 3 из 3] Проверка базы данных..."
if [ ! -f "db.sqlite3" ]; then
    echo "ВНИМАНИЕ: файл db.sqlite3 не найден в папке проекта."
    echo "Запросите его у автора проекта и положите рядом с этим файлом."
    echo ""
else
    echo "База данных найдена."
fi
echo ""

echo "================================================================"
echo "  Установка завершена!"
echo ""
echo "  Для запуска системы выполните:"
echo "  ./start.sh"
echo "================================================================"
echo ""
