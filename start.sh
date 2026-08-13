#!/bin/bash

# Скрипт для запуска и обслуживания приложения калькулятора беременности
# Поддерживает автоматическую проверку обновлений из Git

# Конфигурация
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/venv"
LOG_FILE="/var/log/pdr/startup.log"
SERVICE_NAME="pdr-calc"
BRANCH="${GIT_BRANCH:-main}"
AUTO_UPDATE="${AUTO_UPDATE:-true}"  # true/false - включение автообновления
UPDATE_INTERVAL=86400  # 24 часа в секундах
UPDATE_FLAG_FILE="/tmp/pdr_last_update.check"

# Функция логирования
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    # Пытаемся записать в лог-файл, если есть права
    if [ -w "$(dirname "$LOG_FILE")" ] || [ -w "$LOG_FILE" ]; then
        echo "$msg" >> "$LOG_FILE" 2>/dev/null
    fi
}

log "=== Запуск скрипта обслуживания ==="

# 1. Проверка и установка python3-venv
if ! python3 -c "import venv" &>/dev/null; then
    log "Модуль venv не найден. Установка python3-venv..."
    if command -v apt &>/dev/null; then
        sudo apt update && sudo apt install -y python3-venv python3-pip git
    else
        log "Ошибка: Не удалось установить python3-venv автоматически."
        log "Пожалуйста, установите его вручную: sudo apt install python3-venv"
        exit 1
    fi
fi

# 2. Проверка целостности виртуального окружения
VENV_VALID=false
if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ] && [ -f "$VENV_DIR/bin/python" ] && [ -f "$VENV_DIR/bin/pip" ]; then
    # Дополнительная проверка: запускаем python из venv
    if "$VENV_DIR/bin/python" -c "import sys" &>/dev/null; then
        VENV_VALID=true
        log "Виртуальное окружение найдено и работает корректно."
    else
        log "Виртуальное окружение повреждено (Python не запускается). Требуется пересоздание."
    fi
else
    log "Виртуальное окружение отсутствует или неполное. Требуется создание."
fi

# 3. Создание или пересоздание venv если нужно
if [ "$VENV_VALID" != "true" ]; then
    log "Создание нового виртуального окружения в $VENV_DIR..."
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
    
    if [ $? -ne 0 ]; then
        log "Ошибка создания виртуального окружения!"
        exit 1
    fi
    
    log "Виртуальное окружение успешно создано."
fi

# Активация окружения
source "$VENV_DIR/bin/activate"

# 4. Обновление pip и установка зависимостей
log "Обновление pip и установка зависимостей..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r "$APP_DIR/requirements.txt" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    # Пробуем установить основные пакеты, если requirements.txt нет или ошибка
    log "Попытка установки основных пакетов (Flask, gunicorn)..."
    pip install Flask gunicorn
fi

# 5. Логика автоматического обновления (Auto-Update)
if [ "$AUTO_UPDATE" = "true" ]; then
    NEED_UPDATE=false
    CURRENT_TIME=$(date +%s)
    
    # Проверяем, когда было последнее обновление
    if [ -f "$UPDATE_FLAG_FILE" ]; then
        LAST_UPDATE=$(cat "$UPDATE_FLAG_FILE")
        TIME_DIFF=$((CURRENT_TIME - LAST_UPDATE))
        
        if [ $TIME_DIFF -gt $UPDATE_INTERVAL ]; then
            log "Прошло более 24 часов с последней проверки. Проверка обновлений..."
            NEED_UPDATE=true
        else
            REMAINING=$((UPDATE_INTERVAL - TIME_DIFF))
            log "Следующая проверка обновлений через ${REMAINING} сек."
        fi
    else
        log "Флаг обновления не найден. Выполнение первичной проверки..."
        NEED_UPDATE=true
    fi

    if [ "$NEED_UPDATE" = "true" ]; then
        cd "$APP_DIR"
        
        # Проверяем, является ли директория git-репозиторием
        if [ -d ".git" ]; then
            # Настраиваем remote, если его нет
            if ! git remote get-url origin &>/dev/null; then
                log "Remote origin не настроен. Пропускаем автообновление через git."
            else
                log "Проверка обновлений в репозитории (ветка: $BRANCH)..."
                
                git fetch origin "$BRANCH" 2>/dev/null
                if [ $? -eq 0 ]; then
                    LOCAL=$(git rev-parse HEAD 2>/dev/null)
                    REMOTE=$(git rev-parse "origin/$BRANCH" 2>/dev/null)

                    if [ "$LOCAL" != "$REMOTE" ] && [ -n "$REMOTE" ]; then
                        log "Обнаружены обновления! Локальный: ${LOCAL:0:7}, Удаленный: ${REMOTE:0:7}"
                        log "Выполняем pull и переустановку зависимостей..."
                        
                        git pull origin "$BRANCH"
                        if [ $? -eq 0 ]; then
                            # Переустанавливаем зависимости на случай изменений в requirements.txt
                            pip install -r "$APP_DIR/requirements.txt"
                            
                            # Обновляем timestamp
                            echo "$CURRENT_TIME" > "$UPDATE_FLAG_FILE"
                            
                            # Перезапускаем службу только если скрипт запущен от root или через systemd
                            if [ "$(id -u)" -eq 0 ]; then
                                log "Перезапуск службы $SERVICE_NAME..."
                                systemctl restart "$SERVICE_NAME" 2>/dev/null || true
                                log "Обновление применено, служба перезапущена."
                            else
                                log "Обновление загружено. Для применения требуется перезапуск службы."
                                log "Выполните: sudo systemctl restart $SERVICE_NAME"
                            fi
                            exit 0
                        else
                            log "Ошибка при применении обновлений (git pull failed)."
                        fi
                    else
                        log "Версия актуальна. Обновлений нет."
                        echo "$CURRENT_TIME" > "$UPDATE_FLAG_FILE"
                    fi
                else
                    log "Не удалось получить данные из репозитория (проблемы сети или доступа)."
                fi
            fi
        else
            log "Директория не является git-репозиторием. Автообновление отключено."
        fi
    fi
else
    log "Автоматическое обновление отключено (AUTO_UPDATE=false)."
fi

log "Все проверки завершены. Приложение готово к запуску."

# Если скрипт вызван напрямую (не через systemd), запускаем приложение
if [ "$1" != "--no-start" ]; then
    log "Запуск Gunicorn..."
    exec gunicorn --config "$APP_DIR/gunicorn.conf.py" wsgi:app
fi
