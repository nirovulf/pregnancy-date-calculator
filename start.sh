#!/bin/bash

# Скрипт для запуска приложения калькулятора беременности

echo "Запуск калькулятора беременности..."

# Проверка установки Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не установлен"
    exit 1
fi

# Создание виртуального окружения, если оно не существует
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv "$VENV_DIR"
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
