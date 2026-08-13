#!/bin/bash
#
# Скрипт быстрой установки и запуска PDR Calculator
# Калькулятор ведения беременности в соответствии с клиническими рекомендациями РФ
#
# Использование: sudo ./install.sh
#

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
INSTALL_DIR="/opt/pdr"
SERVICE_NAME="pdr-calc"
SERVICE_FILE="${SERVICE_NAME}.service"
LOG_DIR="/var/log/gunicorn"
USER="www-data"
GROUP="www-data"
PYTHON_VERSION="python3"
VENV_DIR="${INSTALL_DIR}/venv"

# Функция для вывода сообщений
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка прав root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Этот скрипт должен быть запущен от имени root (используйте sudo)"
        exit 1
    fi
}

# Проверка зависимостей
check_dependencies() {
    log_info "Проверка необходимых зависимостей..."
    
    local missing_deps=()
    
    # Проверка Python
    if ! command -v ${PYTHON_VERSION} &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Проверка python3-venv
    if ! ${PYTHON_VERSION} -m venv --help &> /dev/null 2>&1; then
        missing_deps+=("python3-venv")
    fi
    
    # Проверка pip
    if ! ${PYTHON_VERSION} -m pip --help &> /dev/null 2>&1; then
        missing_deps+=("python3-pip")
    fi
    
    # Проверка git (для клонирования репозитория)
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_warning "Отсутствуют следующие пакеты: ${missing_deps[*]}"
        log_info "Установка отсутствующих пакетов..."
        
        if command -v apt-get &> /dev/null; then
            apt-get update -qq
            apt-get install -y -qq ${missing_deps[*]}
        elif command -v yum &> /dev/null; then
            yum install -y ${missing_deps[*]}
        elif command -v dnf &> /dev/null; then
            dnf install -y ${missing_deps[*]}
        else
            log_error "Не удалось найти менеджер пакетов. Установите зависимости вручную."
            exit 1
        fi
    fi
    
    log_success "Все зависимости установлены"
}

# Создание пользователя www-data если не существует
create_user_if_needed() {
    if ! id -u ${USER} &> /dev/null; then
        log_info "Создание пользователя ${USER}..."
        useradd -r -s /usr/sbin/nologin ${USER} || true
    fi
    log_success "Пользователь ${USER} готов"
}

# Создание директорий
create_directories() {
    log_info "Создание директорий..."
    
    mkdir -p ${INSTALL_DIR}
    mkdir -p ${LOG_DIR}
    
    # Установка правильных прав
    chown -R ${USER}:${GROUP} ${INSTALL_DIR}
    chown -R ${USER}:${GROUP} ${LOG_DIR}
    chmod 755 ${INSTALL_DIR}
    
    log_success "Директории созданы: ${INSTALL_DIR}, ${LOG_DIR}"
}

# Установка приложения
install_application() {
    log_info "Установка приложения в ${INSTALL_DIR}..."
    
    # Определение директории со скриптом
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Проверка наличия исходных файлов
    if [ ! -f "${SCRIPT_DIR}/app.py" ] && [ ! -f "${SCRIPT_DIR}/main.py" ]; then
        log_error "Файлы приложения не найдены в ${SCRIPT_DIR}. Убедитесь, что запускаете скрипт из корня проекта."
        exit 1
    fi
    
    # Копирование файлов приложения с использованием rsync для надежности
    log_info "Копирование файлов приложения..."
    if command -v rsync &> /dev/null; then
        rsync -av --exclude='venv' --exclude='__pycache__' --exclude='*.log' --exclude='.git' "${SCRIPT_DIR}/" "${INSTALL_DIR}/"
    else
        # Fallback на cp, если rsync нет
        mkdir -p "${INSTALL_DIR}"
        cp -rT "${SCRIPT_DIR}" "${INSTALL_DIR}"
        # Очистка лишних директорий после копирования
        rm -rf "${INSTALL_DIR}/venv" "${INSTALL_DIR}/__pycache__" "${INSTALL_DIR}/.git"
    fi
    
    # Создание виртуального окружения
    log_info "Создание виртуального окружения Python..."
    ${PYTHON_VERSION} -m venv ${VENV_DIR}
    
    # Активация виртуального окружения и установка зависимостей
    log_info "Установка Python зависимостей..."
    ${VENV_DIR}/bin/pip install --upgrade pip -q
    ${VENV_DIR}/bin/pip install -r ${INSTALL_DIR}/requirements.txt -q
    ${VENV_DIR}/bin/pip install gunicorn -q
    
    # Установка правильных прав
    chown -R ${USER}:${GROUP} ${INSTALL_DIR}
    
    log_success "Приложение установлено"
}

# Настройка конфигурации Gunicorn
configure_gunicorn() {
    log_info "Настройка Gunicorn..."
    
    # Обновление путей в конфигурации Gunicorn
    cat > ${INSTALL_DIR}/gunicorn.conf.py << 'EOF'
"""
Gunicorn configuration file for PDR Calculator
"""
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/pdr-access.log"
errorlog = "/var/log/gunicorn/pdr-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "pdr-calc"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn-pdr.pid"
user = None
group = None
tmp_upload_dir = None
EOF
    
    chown ${USER}:${GROUP} ${INSTALL_DIR}/gunicorn.conf.py
    log_success "Gunicorn настроен"
}

# Установка systemd сервиса
install_systemd_service() {
    log_info "Установка systemd сервиса..."
    
    # Копирование файла сервиса
    cp ${INSTALL_DIR}/${SERVICE_FILE} /etc/systemd/system/${SERVICE_FILE}
    
    # Перезагрузка systemd
    systemctl daemon-reload
    
    # Включение автозапуска
    systemctl enable ${SERVICE_NAME}
    
    log_success "Systemd сервис установлен и включён"
}

# Запуск сервиса
start_service() {
    log_info "Запуск сервиса..."
    
    systemctl start ${SERVICE_NAME}
    
    # Проверка статуса
    sleep 2
    if systemctl is-active --quiet ${SERVICE_NAME}; then
        log_success "Сервис успешно запущен"
    else
        log_error "Не удалось запустить сервис. Проверьте логи: journalctl -u ${SERVICE_NAME}"
        systemctl status ${SERVICE_NAME} --no-pager
        exit 1
    fi
}

# Вывод итоговой информации
show_summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Установка завершена успешно!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Приложение:${NC} PDR Calculator (Калькулятор беременности)"
    echo -e "${BLUE}Директория установки:${NC} ${INSTALL_DIR}"
    echo -e "${BLUE}Сервис:${NC} ${SERVICE_NAME}.service"
    echo -e "${BLUE}Порт:${NC} 5000"
    echo ""
    echo -e "${YELLOW}Полезные команды:${NC}"
    echo "  systemctl status ${SERVICE_NAME}     # Проверка статуса"
    echo "  systemctl restart ${SERVICE_NAME}    # Перезапуск"
    echo "  systemctl stop ${SERVICE_NAME}       # Остановка"
    echo "  journalctl -u ${SERVICE_NAME} -f     # Просмотр логов"
    echo ""
    echo -e "${YELLOW}Доступ к приложению:${NC}"
    echo "  http://localhost:5000"
    echo "  http://<ваш_IP>:5000"
    echo ""
}

# Основная функция
main() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "  PDR Calculator - Установка"
    echo "  Калькулятор ведения беременности"
    echo "=========================================="
    echo -e "${NC}"
    echo ""
    
    check_root
    check_dependencies
    create_user_if_needed
    create_directories
    install_application
    configure_gunicorn
    install_systemd_service
    start_service
    show_summary
}

# Запуск
main "$@"
