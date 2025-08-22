# 🚀 Автоматический хостинг веб-панели управления

## 📋 Содержание
1. [Быстрый старт](#быстрый-старт)
2. [Подготовка проекта](#подготовка-проекта)
3. [Развертывание на Render.com](#развертывание-на-rendercom)
4. [Автоматическое обновление](#автоматическое-обновление)
5. [Мониторинг и уведомления](#мониторинг-и-уведомления)
6. [Резервное копирование](#резервное-копирование)
7. [Безопасность](#безопасность)
8. [Устранение неполадок](#устранение-неполадок)

---

## ⚡ Быстрый старт

### 🎯 Что мы получим в итоге:
- ✅ **Бесплатный хостинг** 24/7 без ограничений
- ✅ **Автоматическое развертывание** при обновлении кода
- ✅ **SSL сертификат** для безопасного соединения
- ✅ **Мониторинг доступности** с уведомлениями
- ✅ **Резервное копирование** данных
- ✅ **Мобильная версия** для управления с телефона

### 🔗 Ваш сайт будет доступен по адресу:
```
https://your-app-name.onrender.com
```

---

## 🔧 Подготовка проекта

### Шаг 1: Создание структуры файлов

```bash
# Создайте новую папку для проекта
mkdir backdoor-dashboard
cd backdoor-dashboard

# Создайте структуру файлов
mkdir web_dashboard
mkdir web_dashboard/templates
mkdir web_dashboard/static
```

### Шаг 2: Основные файлы

**1. `requirements.txt`** - зависимости Python:
```txt
Flask==2.3.3
Flask-SocketIO==5.3.6
python-socketio==5.8.0
python-engineio==4.7.1
Werkzeug==2.3.7
requests==2.31.0
psutil==5.9.5
Pillow==10.0.1
opencv-python==4.8.1.78
cryptography==41.0.4
python-dotenv==1.0.0
gunicorn==21.2.0
eventlet==0.33.3
```

**2. `Procfile`** - для запуска на хостинге:
```
web: gunicorn --worker-class eventlet -w 1 web_dashboard.app:app --bind 0.0.0.0:$PORT
```

**3. `runtime.txt`** - версия Python:
```
python-3.9.18
```

**4. `.gitignore`** - исключения для Git:
```
*.db
__pycache__/
*.pyc
.env
*.log
logs/
backups/
.DS_Store
```

### Шаг 3: Настройка переменных окружения

Создайте файл `.env`:
```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///devices.db
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
FLASK_ENV=production
```

---

## 🌐 Развертывание на Render.com

### Шаг 1: Регистрация и настройка

1. **Зарегистрируйтесь** на [render.com](https://render.com)
2. **Подключите GitHub** аккаунт
3. **Создайте новый репозиторий** на GitHub

### Шаг 2: Загрузка кода

```bash
# Инициализируйте Git репозиторий
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/backdoor-dashboard.git
git push -u origin main
```

### Шаг 3: Создание веб-сервиса на Render

1. **Нажмите "New +"** → **"Web Service"**
2. **Подключите репозиторий** с GitHub
3. **Настройте параметры:**
   - **Name**: `backdoor-dashboard`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 web_dashboard.app:app --bind 0.0.0.0:$PORT`

### Шаг 4: Настройка переменных окружения

В настройках сервиса добавьте:
```
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///devices.db
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
FLASK_ENV=production
```

### Шаг 5: Запуск

Нажмите **"Create Web Service"** и дождитесь завершения развертывания.

---

## 🔄 Автоматическое обновление

### GitHub Actions для автоматического деплоя

Создайте файл `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Render
      uses: johnbeynon/render-deploy-action@v1.0.0
      with:
        service-id: ${{ secrets.RENDER_SERVICE_ID }}
        api-key: ${{ secrets.RENDER_API_KEY }}
```

### Настройка секретов GitHub

1. **Получите Service ID** из настроек Render
2. **Получите API Key** из настроек аккаунта Render
3. **Добавьте секреты** в GitHub репозиторий:
   - `RENDER_SERVICE_ID`
   - `RENDER_API_KEY`

### Автоматические обновления

Теперь при каждом `git push` ваш сайт будет автоматически обновляться!

---

## 📊 Мониторинг и уведомления

### UptimeRobot - бесплатный мониторинг

1. **Зарегистрируйтесь** на [uptimerobot.com](https://uptimerobot.com)
2. **Добавьте новый монитор:**
   - **URL**: `https://your-app-name.onrender.com`
   - **Type**: HTTP(s)
   - **Interval**: 5 minutes
3. **Настройте уведомления** на Telegram/Email

### Встроенный мониторинг

Добавьте в `web_dashboard/app.py`:

```python
import logging
from logging.handlers import RotatingFileHandler
import os

# Настройка логирования
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/backdoor.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Backdoor Dashboard startup')
```

### Telegram уведомления

```python
def send_telegram_notification(message):
    """Отправка уведомления в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": f"🔔 Уведомление с сайта:\n{message}",
            "parse_mode": "HTML"
        }
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        app.logger.error(f"Ошибка отправки уведомления: {e}")
```

---

## 💾 Резервное копирование

### Автоматическое резервное копирование

Создайте файл `backup.py`:

```python
import sqlite3
import shutil
import os
from datetime import datetime
import requests

def backup_database():
    """Создание резервной копии базы данных"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'backups/devices_{timestamp}.db'
        
        # Создаем папку для бэкапов
        os.makedirs('backups', exist_ok=True)
        
        # Копируем базу данных
        shutil.copy2('devices.db', backup_path)
        
        # Отправляем уведомление
        send_telegram_notification(f"✅ Резервная копия создана: {backup_path}")
        
        return backup_path
    except Exception as e:
        send_telegram_notification(f"❌ Ошибка создания бэкапа: {e}")
        return None

def cleanup_old_backups():
    """Удаление старых резервных копий (оставляем последние 10)"""
    try:
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return
            
        files = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        files.sort(reverse=True)
        
        # Удаляем старые файлы
        for old_file in files[10:]:
            os.remove(os.path.join(backup_dir, old_file))
            
    except Exception as e:
        app.logger.error(f"Ошибка очистки старых бэкапов: {e}")
```

### Планировщик задач

Добавьте в `web_dashboard/app.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from backup import backup_database, cleanup_old_backups

# Создаем планировщик
scheduler = BackgroundScheduler()

# Ежедневное резервное копирование в 3:00
scheduler.add_job(backup_database, 'cron', hour=3)
# Еженедельная очистка старых бэкапов
scheduler.add_job(cleanup_old_backups, 'cron', day_of_week='sun', hour=4)

# Запускаем планировщик
scheduler.start()
```

---

## 🔐 Безопасность

### Настройка аутентификации

```python
from functools import wraps
from flask import session, redirect, url_for, request

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Применяем к защищенным маршрутам
@app.route('/admin')
@require_auth
def admin_panel():
    return render_template('admin.html')
```

### Ограничение доступа по IP

```python
ALLOWED_IPS = ['your-ip-address', '127.0.0.1']

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in ALLOWED_IPS:
        return "Access Denied", 403
```

### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Логика входа
    pass
```

### Изменение пароля по умолчанию

```python
def change_default_password():
    """Изменение пароля администратора по умолчанию"""
    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM users WHERE username = "admin"').fetchone()
    
    if admin:
        # Проверяем, не используется ли пароль по умолчанию
        if check_password_hash(admin['password_hash'], 'admin123'):
            # Генерируем новый пароль
            new_password = secrets.token_urlsafe(12)
            password_hash = generate_password_hash(new_password)
            
            conn.execute('UPDATE users SET password_hash = ? WHERE username = ?',
                        (password_hash, 'admin'))
            conn.commit()
            
            send_telegram_notification(f"🔐 Новый пароль администратора: {new_password}")
    
    conn.close()
```

---

## 🔧 Устранение неполадок

### Частые проблемы и решения

#### 1. Ошибка "Module not found"
```bash
# Решение: проверьте requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

#### 2. Ошибка порта
```python
# В web_dashboard/app.py
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
```

#### 3. Проблемы с WebSocket
```python
# Добавьте поддержку WebSocket
socketio.run(app, 
            host='0.0.0.0', 
            port=port, 
            debug=False,
            allow_unsafe_werkzeug=True)
```

#### 4. Ошибки базы данных
```python
# Используйте абсолютные пути
DB_PATH = os.path.join(os.path.dirname(__file__), 'devices.db')
```

#### 5. Проблемы с SSL
```python
# Для локальной разработки
if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'development':
        socketio.run(app, debug=True)
    else:
        socketio.run(app, debug=False)
```

### Логи и отладка

```python
# Добавьте в web_dashboard/app.py
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return "Internal Server Error", 500

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Not Found: {request.url}')
    return "Page Not Found", 404
```

### Проверка работоспособности

Создайте файл `health_check.py`:

```python
import requests
import time

def check_website_health():
    """Проверка работоспособности сайта"""
    try:
        url = "https://your-app-name.onrender.com"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Сайт работает нормально")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    check_website_health()
```

---

## 📱 Мобильная версия

### Адаптивный дизайн

Добавьте в `web_dashboard/templates/base.html`:

```css
/* Мобильная версия */
@media (max-width: 768px) {
    .sidebar {
        position: fixed;
        top: 0;
        left: -100%;
        transition: left 0.3s;
        z-index: 1000;
    }

    .sidebar.show {
        left: 0;
    }

    .main-content {
        margin-left: 0;
    }

    .mobile-menu-toggle {
        display: block;
    }

    .stats-card .stats-number {
        font-size: 1.5rem;
    }
}

/* Кнопка мобильного меню */
.mobile-menu-toggle {
    display: none;
    position: fixed;
    top: 10px;
    left: 10px;
    z-index: 1001;
    background: #667eea;
    border: none;
    color: white;
    padding: 10px;
    border-radius: 5px;
}
```

### JavaScript для мобильного меню

```javascript
// Добавьте в base.html
document.addEventListener('DOMContentLoaded', function() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // Закрытие меню при клике вне его
    document.addEventListener('click', function(e) {
        if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
            sidebar.classList.remove('show');
        }
    });
});
```

---

## 🎯 Итоговая проверка

### Чек-лист готовности

- ✅ [ ] Код загружен в GitHub
- ✅ [ ] Создан веб-сервис на Render.com
- ✅ [ ] Настроены переменные окружения
- ✅ [ ] Сайт доступен по HTTPS
- ✅ [ ] Настроен мониторинг UptimeRobot
- ✅ [ ] Изменен пароль по умолчанию
- ✅ [ ] Настроено резервное копирование
- ✅ [ ] Протестирована мобильная версия

### Тестирование

1. **Откройте сайт** в браузере
2. **Войдите** с новыми учетными данными
3. **Проверьте** все функции
4. **Протестируйте** на мобильном устройстве
5. **Проверьте** уведомления в Telegram

---

## 🚀 Готово!

### Ваш сайт теперь:
- 🌐 **Доступен 24/7** по адресу `https://your-app-name.onrender.com`
- 🔄 **Автоматически обновляется** при изменении кода
- 📱 **Работает на всех устройствах**
- 🔐 **Защищен** SSL сертификатом
- 📊 **Мониторится** с уведомлениями
- 💾 **Резервируется** автоматически

### Доступ к панели:
- **URL**: `https://your-app-name.onrender.com`
- **Логин**: `admin`
- **Пароль**: `[новый пароль из уведомления]`

### Следующие шаги:
1. **Измените пароль** администратора
2. **Настройте** уведомления в Telegram
3. **Добавьте** свои IP в список разрешенных
4. **Протестируйте** все функции

**🎉 Поздравляем! Ваша веб-панель управления готова к работе!**
