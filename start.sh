#!/bin/bash

# Скрипт для запуска приложения калькулятора беременности

echo "Запуск калькулятора беременности..."

# Проверка установки Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не установлен"
    exit 1
fi

# Проверка наличия python3-venv
if ! python3 -c "import venv" &> /dev/null; then
    echo "Ошибка: Модуль venv не доступен. Установите пакет python3-venv:"
    echo "  sudo apt install python3-venv"
    echo ""
    echo "Или для конкретной версии Python (например, 3.12):"
    echo "  sudo apt install python3.12-venv"
    exit 1
fi

# Создание виртуального окружения, если оно не существует
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Ошибка: Не удалось создать виртуальное окружение"
        echo "Убедитесь, что установлен пакет python3-venv:"
        echo "  sudo apt install python3-venv"
        exit 1
    fi
fi

# Активация виртуального окружения
source "$VENV_DIR/bin/activate"

# Установка зависимостей
echo "Установка зависимостей..."
pip install --upgrade pip
pip install Flask gunicorn

# Запуск с помощью gunicorn
echo "Запуск сервера на http://localhost:5000"
gunicorn --config gunicorn.conf.py wsgi:app
