#!/bin/bash

# Скрипт для запуска приложения калькулятора беременности

echo "Запуск калькулятора беременности..."

# Проверка установки Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не установлен"
    exit 1
fi

# Проверка установки pip
if ! command -v pip3 &> /dev/null; then
    echo "Ошибка: pip3 не установлен"
    exit 1
fi

# Установка зависимостей
echo "Установка зависимостей..."
pip3 install Flask gunicorn

# Запуск с помощью gunicorn
echo "Запуск сервера на http://localhost:5000"
gunicorn --config gunicorn.conf.py wsgi:app
