# Калькулятор даты родов

Веб-приложение для расчёта даты родов и связанной информации о беременности на русском языке.

## Особенности

- ✅ AJAX расчёты без перезагрузки страницы
- ✅ Расчёт предполагаемой даты родов
- ✅ Определение текущего срока беременности
- ✅ Рекомендации по прибавке веса на основе BMI
- ✅ Календарь анализов и обследований
- ✅ Таблица норм ХГЧ по неделям
- ✅ Красивый адаптивный интерфейс

## Требования

- Python 3.7+
- Flask
- gunicorn

## Установка и запуск

### 🚀 Автоматическая установка в /opt/pdr (рекомендуется)

**Для установки приложения как systemd-сервиса:**

```bash
sudo ./install.sh
```

Скрипт автоматически:
- Проверит и установит необходимые зависимости (Python 3, pip, venv)
- Создаст виртуальное окружение в `/opt/pdr/venv`
- Установит все зависимости Python
- Настроит Gunicorn с оптимальными параметрами
- Установит и активирует systemd-сервис `pdr-calc.service`
- Запустит приложение

После установки приложение будет доступно по адресу: `http://localhost:5000`

**Управление сервисом:**
```bash
systemctl status pdr-calc     # Проверка статуса
systemctl restart pdr-calc    # Перезапуск
systemctl stop pdr-calc       # Остановка
journalctl -u pdr-calc -f     # Просмотр логов в реальном времени
```

### Локальный запуск (для разработки)

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
start.bat
```

### Ручная установка

1. **Установите зависимости:**
   ```bash
   pip install Flask gunicorn
   ```

2. **Запустите приложение:**

   **Режим разработки:**
   ```bash
   python main.py
   ```

   **Продакшен с gunicorn:**
   ```bash
   gunicorn --config gunicorn.conf.py wsgi:app
   ```

   **Простой запуск с gunicorn:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
   ```

3. **Откройте браузер** и перейдите на `http://localhost:5000`

## Структура проекта

```
pregnancy_calculator/
├── main.py              # Основное приложение Flask
├── wsgi.py              # WSGI точка входа для gunicorn
├── gunicorn.conf.py     # Конфигурация gunicorn
├── install.sh           # Скрипт автоматической установки в /opt/pdr
├── start.sh             # Скрипт запуска для Linux/macOS
├── start.bat            # Скрипт запуска для Windows
├── pdr-calc.service     # systemd unit файл для сервиса
├── requirements.txt     # Python зависимости
├── templates/
│   └── index.html       # HTML шаблон
└── static/
    ├── style.css        # Стили CSS
    └── script.js        # JavaScript логика
```

## Конфигурация gunicorn

Файл `gunicorn.conf.py` содержит оптимальные настройки для продакшена:

- **Воркеры:** автоматически по количеству CPU ядер
- **Порт:** 5000
- **Логирование:** вывод в консоль
- **Таймауты:** оптимизированы для веб-приложения

## Кастомизация

### Изменение порта

В `gunicorn.conf.py`:
```python
bind = "0.0.0.0:8080"  # изменить порт на 8080
```

### Изменение количества воркеров

В `gunicorn.conf.py`:
```python
workers = 2  # фиксированное количество воркеров
```

### Добавление в systemd

**Автоматическая установка (рекомендуется):**
```bash
sudo ./install.sh
```

**Ручная установка:**

1. Скопируйте файл сервиса:
```bash
sudo cp pdr-calc.service /etc/systemd/system/
```

2. Отредактируйте пути в файле сервиса при необходимости:
- `WorkingDirectory` - путь к директории приложения (по умолчанию `/opt/pdr`)
- `ExecStart` - путь к gunicorn и конфигурации

3. Создайте директорию для логов и установите права:
```bash
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
sudo chmod 755 /opt/pdr
```

4. Активируйте и запустите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pdr-calc
sudo systemctl start pdr-calc
```

5. Проверьте статус:
```bash
systemctl status pdr-calc
```

## API

### POST /api/calculate

Рассчитывает данные беременности.

**Параметры:**
- `last_period` (обязательный) - дата последней менструации (YYYY-MM-DD)
- `cycle_length` (опциональный) - длина цикла в днях (по умолчанию 28)
- `pre_pregnancy_weight` (опциональный) - вес до беременности в кг
- `height` (опциональный) - рост в см

**Ответ:**
```json
{
  "success": true,
  "data": {
    "conceptionDate": "дата зачатия",
    "dueDate": "предполагаемая дата родов",
    "pregnancyWeeks": 12,
    "pregnancyDaysRemainder": 3,
    "daysUntilBirth": 196,
    "currentTrimester": "1 триместр",
    "maternityLeaveDate": "дата декретного отпуска",
    "weightGainRange": "11.5-16 кг",
    "testDates": [...],
    "hcgLevels": [...]
  }
}
```

## Лицензия

MIT License
