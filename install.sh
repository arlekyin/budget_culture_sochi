#!/bin/bash
cd "$(dirname "$0")"

echo ""
echo "================================================================"
echo "  Установка системы «Бюджет-Культура Сочи»"
echo "================================================================"
echo ""

# Ищем подходящий Python (3.11 или 3.12) — сначала Homebrew, потом системный
PYTHON_CMD=""
for candidate in \
    /opt/homebrew/bin/python3.12 \
    /opt/homebrew/bin/python3.11 \
    /usr/local/bin/python3.12 \
    /usr/local/bin/python3.11 \
    python3.12 \
    python3.11; do
    if command -v "$candidate" &>/dev/null; then
        PYTHON_CMD="$candidate"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    if ! command -v python3 &>/dev/null; then
        echo "ОШИБКА: Python 3.11 или 3.12 не найден."
        echo ""
        echo "Установите через Homebrew:"
        echo "  brew install python@3.11"
        echo ""
        read -p "Нажмите Enter для выхода..."
        exit 1
    fi
    PYTHON_CMD="python3"
fi

PYTHON_MINOR=$("$PYTHON_CMD" -c "import sys; print(sys.version_info.minor)")
PYTHON_MAJOR=$("$PYTHON_CMD" -c "import sys; print(sys.version_info.major)")

echo "Python найден: $("$PYTHON_CMD" --version)"

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; then
    echo ""
    echo "ОШИБКА: Python $("$PYTHON_CMD" --version) слишком старый."
    echo "Требуется Python 3.11 или 3.12."
    echo ""
    echo "Установите через Homebrew:"
    echo "  brew install python@3.11"
    echo ""
    echo "Затем удалите папку venv и запустите снова:"
    echo "  rm -rf venv && ./install.sh"
    echo ""
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 13 ]; then
    echo ""
    echo "ОШИБКА: Python $("$PYTHON_CMD" --version) не поддерживается."
    echo "Требуется Python 3.11 или 3.12."
    echo ""
    echo "Установите через Homebrew:"
    echo "  brew install python@3.11"
    echo ""
    echo "Затем удалите папку venv и запустите снова:"
    echo "  rm -rf venv && ./install.sh"
    echo ""
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

echo ""

# Виртуальная среда
echo "[Шаг 1 из 3] Подготовка рабочей среды Python..."
if [ ! -d "venv" ]; then
    "$PYTHON_CMD" -m venv venv
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

# База данных
echo "[Шаг 3 из 3] Подготовка базы данных..."
if [ ! -f "db.sqlite3" ]; then
    echo "База данных не найдена — создаём с нуля..."
    python manage.py migrate -v 0
    if [ $? -ne 0 ]; then
        echo "ОШИБКА при создании базы данных."
        read -p "Нажмите Enter для выхода..."
        exit 1
    fi
    python manage.py create_demo_data
    if [ $? -ne 0 ]; then
        echo "ОШИБКА при загрузке демо-данных."
        read -p "Нажмите Enter для выхода..."
        exit 1
    fi
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
