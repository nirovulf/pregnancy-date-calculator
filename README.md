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

### Автоматический запуск

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
├── start.sh             # Скрипт запуска для Linux/macOS
├── start.bat            # Скрипт запуска для Windows
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
В файле pdr-calc.service указать актуальные пути, дать права на запись пользователю www-data на каталог с логами и каталог с файлами приложения

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
