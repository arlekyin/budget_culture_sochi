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

# Если не нашли — пробуем общий python3 и проверяем версию
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
echo "[Шаг 1 из 4] Подготовка рабочей среды Python..."
if [ ! -d "venv" ]; then
    "$PYTHON_CMD" -m venv venv
fi
source venv/bin/activate
echo "Готово."
echo ""

# Установка зависимостей Python
echo "[Шаг 2 из 4] Установка компонентов Python (2-5 минут)..."
pip install -r requirements.txt -q --no-warn-script-location
if [ $? -ne 0 ]; then
    echo "ОШИБКА при установке. Проверьте подключение к интернету."
    read -p "Нажмите Enter для выхода..."
    exit 1
fi
echo "Готово."
echo ""

# Сборка фронтенда
echo "[Шаг 3 из 4] Сборка интерфейса (требуется Node.js)..."
if ! command -v node &>/dev/null; then
    echo "ОШИБКА: Node.js не найден."
    echo ""
    echo "Установите его с официального сайта:"
    echo "https://nodejs.org/"
    echo ""
    echo "Или через Homebrew:"
    echo "  brew install node"
    echo ""
    echo "После установки запустите ./install.sh снова."
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

echo "Node.js найден: $(node --version)"
cd frontend
npm install --silent
if [ $? -ne 0 ]; then
    echo "ОШИБКА при установке npm-зависимостей."
    read -p "Нажмите Enter для выхода..."
    exit 1
fi
npm run build
if [ $? -ne 0 ]; then
    echo "ОШИБКА при сборке интерфейса."
    read -p "Нажмите Enter для выхода..."
    exit 1
fi
cd ..
echo "Готово."
echo ""

# База данных
echo "[Шаг 4 из 4] Подготовка базы данных..."
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
