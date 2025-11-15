from flask import Flask, request, session, redirect, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'test'

USERS_FILE = 'users.txt'
MESSAGES_FILE = 'messages.txt'

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_messages(messages):
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f)

users = load_users()
if not users:
    users = {'admin': 'admin123'}
    save_users(users)

messages = load_messages()
if not messages:
    messages = ['Система: Чат запущен!']
    save_messages(messages)

# API для получения сообщений
@app.route('/api/messages')
def api_messages():
    if 'user' not in session:
        return jsonify({'error': 'Not authorized'}), 401
    return jsonify({'messages': messages[-50:]})

# API для удаления пользователя
@app.route('/admin/delete-user/<username>')
def delete_user(username):
    if 'user' not in session or session['user'] != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    if username == 'admin':
        return jsonify({'error': 'Нельзя удалить администратора'}), 400
    
    if username in users:
        del users[username]
        save_users(users)
        messages.append(f'Система: Пользователь {username} был удален администратором')
        save_messages(messages)
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Пользователь не найден'}), 404

# API для очистки чата
@app.route('/admin/clear-chat')
def clear_chat():
    if 'user' not in session or session['user'] != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    global messages
    messages = ['Система: История чата очищена администратором']
    save_messages(messages)
    return jsonify({'success': True})

# Главная страница
@app.route('/')
def home():
    if 'user' in session:
        is_admin = session['user'] == 'admin'
        admin_button = '<a href="/admin" class="btn btn-admin">👑 Админ-панель</a>' if is_admin else ''
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>💬 Умный Чат</title>
            <style>
                :root {{
                    --bg-primary: #0f0f23;
                    --bg-secondary: #1a1a2e;
                    --bg-card: #16213e;
                    --accent: #7b68ee;
                    --accent-hover: #6a5acd;
                    --text-primary: #e2e8f0;
                    --text-secondary: #94a3b8;
                    --success: #10b981;
                    --danger: #ef4444;
                    --warning: #f59e0b;
                }}
                
                body {{
                    font-family: 'Arial', sans-serif;
                    background: var(--bg-primary);
                    margin: 0;
                    padding: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: var(--text-primary);
                }}
                .container {{
                    background: var(--bg-card);
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                    padding: 40px;
                    max-width: 500px;
                    width: 90%;
                    border: 1px solid #2d3748;
                }}
                .welcome {{
                    background: linear-gradient(135deg, var(--accent) 0%, #4c1d95 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 30px;
                    margin: 10px;
                    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 25px;
                    border: none;
                    cursor: pointer;
                    font-size: 16px;
                    transition: all 0.3s;
                    box-shadow: 0 4px 15px rgba(123, 104, 238, 0.3);
                }}
                .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(123, 104, 238, 0.5);
                }}
                .btn-danger {{
                    background: linear-gradient(135deg, var(--danger) 0%, #dc2626 100%);
                }}
                .btn-admin {{
                    background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%);
                }}
                .admin-badge {{
                    background: var(--warning);
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 12px;
                    margin-left: 10px;
                }}
                .theme-toggle {{
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: var(--bg-secondary);
                    border: none;
                    color: var(--text-primary);
                    padding: 10px 15px;
                    border-radius: 20px;
                    cursor: pointer;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <button class="theme-toggle" onclick="toggleTheme()">🌙 Тёмная тема</button>
            <div class="container">
                <h1>💬 Умный Чат</h1>
                <div class="welcome">
                    <h2>👋 Привет, {session['user']}! 
                        {'<span class="admin-badge">ADMIN</span>' if is_admin else ''}
                    </h2>
                    <p>Рады видеть вас снова!</p>
                </div>
                <div style="text-align: center;">
                    <a href="/chat" class="btn">🚀 Войти в чат</a>
                    {admin_button}
                    <a href="/logout" class="btn btn-danger">🚪 Выйти</a>
                </div>
            </div>
            <script>
                function toggleTheme() {{
                    document.body.style.filter = document.body.style.filter ? '' : 'invert(1) hue-rotate(180deg)';
                }}
            </script>
        </body>
        </html>
        '''
    else:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>💬 Умный Чат</title>
            <style>
                :root {
                    --bg-primary: #0f0f23;
                    --bg-secondary: #1a1a2e;
                    --bg-card: #16213e;
                    --accent: #7b68ee;
                    --accent-hover: #6a5acd;
                    --text-primary: #e2e8f0;
                    --text-secondary: #94a3b8;
                }
                
                body {
                    font-family: 'Arial', sans-serif;
                    background: var(--bg-primary);
                    margin: 0;
                    padding: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: var(--text-primary);
                }
                .container {
                    background: var(--bg-card);
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                    padding: 40px;
                    max-width: 400px;
                    width: 90%;
                    border: 1px solid #2d3748;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .btn {
                    display: block;
                    width: 200px;
                    padding: 15px;
                    margin: 15px auto;
                    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 25px;
                    text-align: center;
                    font-size: 16px;
                    transition: all 0.3s;
                    box-shadow: 0 4px 15px rgba(123, 104, 238, 0.3);
                }
                .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(123, 104, 238, 0.5);
                }
                .demo {
                    background: var(--bg-secondary);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    margin-top: 20px;
                    border: 1px solid #374151;
                }
                .theme-toggle {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: var(--bg-secondary);
                    border: none;
                    color: var(--text-primary);
                    padding: 10px 15px;
                    border-radius: 20px;
                    cursor: pointer;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <button class="theme-toggle" onclick="toggleTheme()">🌙 Тёмная тема</button>
            <div class="container">
                <div class="header">
                    <h1 style="margin-bottom: 10px;">💬 Умный Чат</h1>
                    <p style="color: var(--text-secondary);">Общайтесь безопасно и удобно</p>
                </div>
                <a href="/login" class="btn">🔐 Войти в систему</a>
                <a href="/register" class="btn">👤 Создать аккаунт</a>
                <div class="demo">
            <script>
                function toggleTheme() {
                    document.body.style.filter = document.body.style.filter ? '' : 'invert(1) hue-rotate(180deg)';
                }
            </script>
        </body>
        </html>
        '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username] == password:
            session['user'] = username
            messages.append(f'Система: {username} вошел в чат')
            save_messages(messages)
            return redirect('/')
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ошибка входа</title>
            <style>
                :root {
                    --bg-primary: #0f0f23;
                    --bg-secondary: #1a1a2e;
                    --danger: #ef4444;
                    --text-primary: #e2e8f0;
                }
                body { 
                    font-family: Arial; 
                    background: var(--bg-primary); 
                    padding: 50px; 
                    text-align: center; 
                    color: var(--text-primary);
                }
                .error { 
                    background: var(--danger); 
                    color: white; 
                    padding: 20px; 
                    border-radius: 10px; 
                    display: inline-block; 
                }
                a { color: white; }
            </style>
        </head>
        <body>
            <div class="error">
                <h2>❌ Ошибка входа</h2>
                <p>Неверный логин или пароль</p>
                <a href="/login">Попробовать снова</a>
            </div>
        </body>
        </html>
        '''
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Вход в систему</title>
        <style>
            :root {
                --bg-primary: #0f0f23;
                --bg-secondary: #1a1a2e;
                --bg-card: #16213e;
                --accent: #7b68ee;
                --accent-hover: #6a5acd;
                --text-primary: #e2e8f0;
                --text-secondary: #94a3b8;
                --border: #374151;
            }
            
            body {
                font-family: 'Arial', sans-serif;
                background: var(--bg-primary);
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--text-primary);
            }
            .container {
                background: var(--bg-card);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                padding: 40px;
                max-width: 400px;
                width: 90%;
                border: 1px solid var(--border);
            }
            .form-group {
                margin-bottom: 20px;
            }
            input {
                width: 100%;
                padding: 15px;
                background: var(--bg-secondary);
                border: 2px solid var(--border);
                border-radius: 10px;
                font-size: 16px;
                box-sizing: border-box;
                color: var(--text-primary);
            }
            input:focus {
                border-color: var(--accent);
                outline: none;
            }
            input::placeholder {
                color: var(--text-secondary);
            }
            .btn {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(123, 104, 238, 0.3);
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(123, 104, 238, 0.5);
            }
            a {
                color: var(--accent);
                text-decoration: none;
            }
            .theme-toggle {
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--bg-secondary);
                border: none;
                color: var(--text-primary);
                padding: 10px 15px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <button class="theme-toggle" onclick="toggleTheme()">🌙 Тёмная тема</button>
        <div class="container">
            <h1 style="text-align: center; margin-bottom: 30px;">🔐 Вход в систему</h1>
            <form method="POST">
                <div class="form-group">
                    <input type="text" name="username" placeholder="👤 Введите логин" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="🔒 Введите пароль" required>
                </div>
                <button type="submit" class="btn">Войти в систему</button>
            </form>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/">← Назад на главную</a>
            </div>
        </div>
        <script>
            function toggleTheme() {
                document.body.style.filter = document.body.style.filter ? '' : 'invert(1) hue-rotate(180deg)';
            }
        </script>
    </body>
    </html>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    :root {
                        --bg-primary: #0f0f23;
                        --danger: #ef4444;
                        --text-primary: #e2e8f0;
                    }
                    body { 
                        background: var(--bg-primary); 
                        color: var(--text-primary); 
                        text-align: center; 
                        padding: 50px; 
                    }
                    a { color: var(--danger); }
                </style>
            </head>
            <body>
                <h2>❌ Пользователь уже существует!</h2>
                <a href="/register">Назад</a>
            </body>
            </html>
            '''
        
        users[username] = password
        save_users(users)
        session['user'] = username
        messages.append(f'Система: {username} зарегистрировался')
        save_messages(messages)
        return redirect('/chat')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Регистрация</title>
        <style>
            :root {
                --bg-primary: #0f0f23;
                --bg-secondary: #1a1a2e;
                --bg-card: #16213e;
                --accent: #7b68ee;
                --accent-hover: #6a5acd;
                --text-primary: #e2e8f0;
                --text-secondary: #94a3b8;
                --border: #374151;
            }
            
            body {
                font-family: 'Arial', sans-serif;
                background: var(--bg-primary);
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--text-primary);
            }
            .container {
                background: var(--bg-card);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                padding: 40px;
                max-width: 400px;
                width: 90%;
                border: 1px solid var(--border);
            }
            .form-group {
                margin-bottom: 20px;
            }
            input {
                width: 100%;
                padding: 15px;
                background: var(--bg-secondary);
                border: 2px solid var(--border);
                border-radius: 10px;
                font-size: 16px;
                box-sizing: border-box;
                color: var(--text-primary);
            }
            input::placeholder {
                color: var(--text-secondary);
            }
            .btn {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(123, 104, 238, 0.3);
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(123, 104, 238, 0.5);
            }
            a {
                color: var(--accent);
            }
            .theme-toggle {
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--bg-secondary);
                border: none;
                color: var(--text-primary);
                padding: 10px 15px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <button class="theme-toggle" onclick="toggleTheme()">🌙 Тёмная тема</button>
        <div class="container">
            <h1 style="text-align: center; color: var(--text-primary); margin-bottom: 30px;">👤 Регистрация</h1>
            <form method="POST">
                <div class="form-group">
                    <input type="text" name="username" placeholder="Придумайте логин" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Придумайте пароль" required>
                </div>
                <button type="submit" class="btn">Создать аккаунт</button>
            </form>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/">← Назад на главную</a>
            </div>
        </div>
        <script>
            function toggleTheme() {
                document.body.style.filter = document.body.style.filter ? '' : 'invert(1) hue-rotate(180deg)';
            }
        </script>
    </body>
    </html>
    '''

# МАРШРУТ ЧАТА - ДОБАВЛЯЕМ ЕГО
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        message = request.form['message']
        if message.strip():
            timestamp = datetime.now().strftime("%H:%M")
            messages.append(f"[{timestamp}] {session['user']}: {message}")
            save_messages(messages)
        return redirect('/chat')
    
    chat_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>💬 Чат</title>
        <style>
            :root {
                --bg-primary: #0f0f23;
                --bg-secondary: #1a1a2e;
                --bg-card: #16213e;
                --accent: #7b68ee;
                --accent-hover: #6a5acd;
                --text-primary: #e2e8f0;
                --text-secondary: #94a3b8;
                --border: #374151;
                --system-bg: #1e3a8a;
                --user-bg: #3730a3;
            }
            
            body {
                font-family: 'Arial', sans-serif;
                background: var(--bg-primary);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                color: var(--text-primary);
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: var(--bg-card);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                overflow: hidden;
                border: 1px solid var(--border);
            }
            .header {
                background: linear-gradient(135deg, var(--accent) 0%, #4c1d95 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .messages {
                height: 500px;
                overflow-y: auto;
                padding: 20px;
                background: var(--bg-primary);
            }
            .message {
                margin: 10px 0;
                padding: 15px;
                border-radius: 15px;
                max-width: 80%;
                word-wrap: break-word;
                opacity: 0;
                animation: fadeIn 0.3s ease-in forwards;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .system {
                background: var(--system-bg);
                margin: 0 auto;
                text-align: center;
                color: #bfdbfe;
                border: 1px solid #3b82f6;
            }
            .user {
                background: var(--user-bg);
                margin-left: auto;
                color: #c7d2fe;
                border: 1px solid #6366f1;
            }
            .other-user {
                background: var(--bg-secondary);
                margin-right: auto;
                color: var(--text-primary);
                border: 1px solid var(--border);
            }
            .form-container {
                padding: 20px;
                background: var(--bg-card);
                border-top: 1px solid var(--border);
            }
            input {
                width: 70%;
                padding: 15px;
                background: var(--bg-secondary);
                border: 2px solid var(--border);
                border-radius: 25px;
                font-size: 16px;
                color: var(--text-primary);
            }
            input::placeholder {
                color: var(--text-secondary);
            }
            .btn {
                padding: 15px 30px;
                background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                margin-left: 10px;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(123, 104, 238, 0.3);
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(123, 104, 238, 0.5);
            }
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            a {
                color: var(--accent);
                text-decoration: none;
            }
            .theme-toggle {
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--bg-secondary);
                border: none;
                color: var(--text-primary);
                padding: 10px 15px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                z-index: 1000;
            }
            
            .messages::-webkit-scrollbar {
                width: 8px;
            }
            .messages::-webkit-scrollbar-track {
                background: var(--bg-secondary);
                border-radius: 4px;
            }
            .messages::-webkit-scrollbar-thumb {
                background: var(--accent);
                border-radius: 4px;
            }
            
            .status {
                text-align: center;
                padding: 10px;
                color: var(--text-secondary);
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <button class="theme-toggle" onclick="toggleTheme()">🌙 Тёмная тема</button>
        <div class="container">
            <div class="header">
                <h1>💬 Умный Чат</h1>
                <p>Вы вошли как: <strong>''' + session['user'] + '''</strong></p>
                <div class="status" id="status">🟢 Онлайн</div>
            </div>
            <div class="messages" id="messagesContainer">
    '''
    
    for msg in messages[-50:]:
        if 'Система:' in msg:
            chat_html += f'<div class="message system">🔔 {msg}</div>'
        elif session['user'] in msg:
            chat_html += f'<div class="message user">{msg}</div>'
        else:
            chat_html += f'<div class="message other-user">{msg}</div>'
    
    chat_html += '''
            </div>
            <div class="form-container">
                <form id="messageForm" method="POST" style="display: flex;">
                    <input type="text" name="message" id="messageInput" placeholder="Напишите сообщение..." required autocomplete="off">
                    <button type="submit" class="btn" id="sendButton">📤 Отправить</button>
                </form>
                <div style="text-align: center; margin-top: 15px;">
                    <a href="/">← Назад на главную</a>
                </div>
            </div>
        </div>
        <script>
            let currentUser = "''' + session['user'] + '''";
            let lastMessageCount = ''' + str(len(messages)) + ''';
            let autoRefreshEnabled = true;
            
            function addMessageToChat(message, isSystem = false, isCurrentUser = false) {
                const messagesContainer = document.getElementById('messagesContainer');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message';
                
                if (isSystem) {
                    messageDiv.className += ' system';
                    messageDiv.innerHTML = '🔔 ' + message;
                } else if (isCurrentUser) {
                    messageDiv.className += ' user';
                    messageDiv.textContent = message;
                } else {
                    messageDiv.className += ' other-user';
                    messageDiv.textContent = message;
                }
                
                messagesContainer.appendChild(messageDiv);
                
                setTimeout(() => {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }, 100);
            }
            
            async function loadNewMessages() {
                if (!autoRefreshEnabled) return;
                
                try {
                    const response = await fetch('/api/messages');
                    const data = await response.json();
                    
                    if (data.messages && data.messages.length > lastMessageCount) {
                        for (let i = lastMessageCount; i < data.messages.length; i++) {
                            const msg = data.messages[i];
                            const isSystem = msg.includes('Система:');
                            const isCurrentUser = msg.includes(currentUser + ':') || msg.includes('[' + currentUser + ']');
                            addMessageToChat(msg, isSystem, isCurrentUser);
                        }
                        lastMessageCount = data.messages.length;
                        document.getElementById('status').textContent = '🟢 Онлайн • ' + new Date().toLocaleTimeString();
                    }
                } catch (error) {
                    console.error('Ошибка загрузки сообщений:', error);
                    document.getElementById('status').textContent = '🔴 Ошибка соединения';
                }
            }
            
            async function sendMessage(message) {
                const formData = new FormData();
                formData.append('message', message);
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        loadNewMessages();
                    }
                } catch (error) {
                    console.error('Ошибка отправки сообщения:', error);
                    alert('Ошибка отправки сообщения');
                }
            }
            
            document.getElementById('messageForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const messageInput = document.getElementById('messageInput');
                const message = messageInput.value.trim();
                
                if (message) {
                    const sendButton = document.getElementById('sendButton');
                    sendButton.disabled = true;
                    sendButton.textContent = '⏳...';
                    
                    sendMessage(message).finally(() => {
                        sendButton.disabled = false;
                        sendButton.textContent = '📤 Отправить';
                        messageInput.value = '';
                        messageInput.focus();
                    });
                }
            });
            
            setInterval(loadNewMessages, 2000);
            
            document.addEventListener('DOMContentLoaded', function() {
                loadNewMessages();
                document.getElementById('messageInput').focus();
                const messagesContainer = document.getElementById('messagesContainer');
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            });
            
            document.addEventListener('visibilitychange', function() {
                autoRefreshEnabled = !document.hidden;
                if (autoRefreshEnabled) {
                    loadNewMessages();
                }
            });
            
            function toggleTheme() {
                document.body.style.filter = document.body.style.filter ? '' : 'invert(1) hue-rotate(180deg)';
            }
            
            document.getElementById('messageInput').addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    document.getElementById('messageForm').dispatchEvent(new Event('submit'));
                }
            });
        </script>
    </body>
    </html>
    '''
    return chat_html

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')
    
    if session['user'] != 'admin':
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Доступ запрещен</title>
            <style>
                :root {
                    --bg-primary: #0f0f23;
                    --bg-secondary: #1a1a2e;
                    --danger: #ef4444;
                    --text-primary: #e2e8f0;
                }
                body { 
                    font-family: Arial; 
                    background: var(--bg-primary); 
                    padding: 50px; 
                    text-align: center; 
                    color: var(--text-primary);
                }
                .error { 
                    background: var(--danger); 
                    color: white; 
                    padding: 20px; 
                    border-radius: 10px; 
                    display: inline-block; 
                }
                a { color: white; }
            </style>
        </head>
        <body>
            <div class="error">
                <h2>⛔ Доступ запрещен</h2>
                <p>Только администратор может просматривать эту страницу</p>
                <a href="/">На главную</a>
            </div>
        </body>
        </html>
        '''
    
    all_users = load_users()
    all_messages = load_messages()
    
    total_users = len(all_users)
    total_messages = len(all_messages)
    
    admin_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>👑 Админ-панель</title>
        <style>
            :root {{
                --bg-primary: #0f0f23;
                --bg-secondary: #1a1a2e;
                --bg-card: #16213e;
                --accent: #7b68ee;
                --accent-hover: #6a5acd;
                --text-primary: #e2e8f0;
                --text-secondary: #94a3b8;
                --success: #10b981;
                --danger: #ef4444;
                --warning: #f59e0b;
                --border: #374151;
            }}
            
            body {{
                font-family: 'Arial', sans-serif;
                background: var(--bg-primary);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                color: var(--text-primary);
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{
                background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%);
                color: white;
                padding: 30px;
                border-radius: 20px;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(245, 158, 11, 0.3);
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: var(--bg-card);
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                border: 1px solid var(--border);
                transition: transform 0.3s;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }}
            .users {{
                background: var(--bg-card);
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 20px;
                border: 1px solid var(--border);
            }}
            .messages-preview {{
                background: var(--bg-card);
                padding: 25px;
                border-radius: 15px;
                border: 1px solid var(--border);
            }}
            .user-list {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 10px;
                margin-top: 15px;
            }}
            .user-item {{
                background: var(--bg-secondary);
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid var(--accent);
                position: relative;
            }}
            .admin-user {{
                border-left-color: var(--warning);
                background: linear-gradient(135deg, var(--bg-secondary) 0%, #422006 100%);
            }}
            .delete-btn {{
                position: absolute;
                top: 5px;
                right: 5px;
                background: var(--danger);
                color: white;
                border: none;
                border-radius: 50%;
                width: 25px;
                height: 25px;
                cursor: pointer;
                font-size: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0.7;
                transition: opacity 0.3s;
            }}
            .delete-btn:hover {{
                opacity: 1;
                transform: scale(1.1);
            }}
            .message-item {{
                background: var(--bg-secondary);
                padding: 12px;
                margin: 8px 0;
                border-radius: 8px;
                border-left: 3px solid var(--success);
                font-size: 0.9em;
            }}
            .system-message {{
                border-left-color: var(--accent);
                background: var(--bg-primary);
            }}
            .btn {{
                display: inline-block;
                padding: 12px 25px;
                margin: 10px 5px;
                background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
                color: white;
                text-decoration: none;
                border-radius: 25px;
                border: none;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(123, 104, 238, 0.4);
            }}
            .btn-danger {{
                background: linear-gradient(135deg, var(--danger) 0%, #dc2626 100%);
            }}
            .btn-warning {{
                background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%);
            }}
            .actions {{
                text-align: center;
                margin: 20px 0;
            }}
            .theme-toggle {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--bg-secondary);
                border: none;
                color: var(--text-primary);
                padding: 10px 15px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                z-index: 1000;
            }}
            .section-title {{
                color: var(--text-primary);
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid var(--border);
            }}
            .notification {{
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                padding: 15px 25px;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                z-index: 1001;
                opacity: 0;
                transition: opacity 0.3s;
            }}
            .notification.success {{
                background: var(--success);
            }}
            .notification.error {{
                background: var(--danger);
            }}
            .notification.show {{
                opacity: 1;
            }}
        </style>
    </head>
    <body>
        <button class="theme-toggle" onclick="toggleTheme()">🌙 Тёмная тема</button>
        
        <div id="notification" class="notification"></div>
        
        <div class="container">
            <div class="header">
                <h1>👑 Админ-панель</h1>
                <p>Управление системой чата</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>👥 Пользователи</h3>
                    <div class="stat-number">{total_users}</div>
                    <p>зарегистрировано</p>
                </div>
                <div class="stat-card">
                    <h3>💬 Сообщения</h3>
                    <div class="stat-number">{total_messages}</div>
                    <p>всего отправлено</p>
                </div>
                <div class="stat-card">
                    <h3>🟢 Активность</h3>
                    <div class="stat-number">{len(all_users)}</div>
                    <p>активных пользователей</p>
                </div>
            </div>
            
            <div class="actions">
                <button class="btn btn-danger" onclick="clearChat()">🗑️ Очистить весь чат</button>
                <a href="/" class="btn">🏠 На главную</a>
                <a href="/chat" class="btn">💬 Перейти в чат</a>
            </div>
            
            <div class="users">
                <h2 class="section-title">📊 Управление пользователями</h2>
                <div class="user-list">
    '''
    
    for username in all_users.keys():
        is_admin = username == 'admin'
        admin_class = 'admin-user' if is_admin else ''
        admin_badge = ' 👑' if is_admin else ''
        delete_button = '' if is_admin else f'<button class="delete-btn" onclick="deleteUser(\'{username}\')">×</button>'
        
        admin_html += f'''
                    <div class="user-item {admin_class}">
                        {delete_button}
                        <strong>{username}{admin_badge}</strong>
                        <br>
                        <small style="color: var(--text-secondary);">
                            {len([m for m in all_messages if m.split(':')[0].strip().endswith(username)])} сообщ.
                        </small>
                    </div>
        '''
    
    admin_html += '''
                </div>
            </div>
            
            <div class="messages-preview">
                <h2 class="section-title">📝 Последние сообщения</h2>
    '''
    
    for msg in all_messages[-10:]:
        message_class = 'system-message' if 'Система:' in msg else ''
        admin_html += f'<div class="message-item {message_class}">{msg}</div>'
    
    admin_html += '''
            </div>
        </div>
        
        <script>
            function showNotification(message, type = 'success') {
                const notification = document.getElementById('notification');
                notification.textContent = message;
                notification.className = `notification ${type} show`;
                
                setTimeout(() => {
                    notification.classList.remove('show');
                }, 3000);
            }
            
            async function deleteUser(username) {
                if (!confirm(`Вы уверены, что хотите удалить пользователя "${username}"?`)) {
                    return;
                }
                
                try {
                    const response = await fetch(`/admin/delete-user/${username}`);
                    const data = await response.json();
                    
                    if (data.success) {
                        showNotification(`Пользователь "${username}" удален`, 'success');
                        setTimeout(() => {
                            location.reload();
                        }, 1000);
                    } else {
                        showNotification(data.error || 'Ошибка удаления', 'error');
                    }
                } catch (error) {
                    showNotification('Ошибка соединения', 'error');
                }
            }
            
            async function clearChat() {
                if (!confirm('Вы уверены, что хотите очистить всю историю чата? Это действие нельзя отменить.')) {
                    return;
                }
                
                try {
                    const response = await fetch('/admin/clear-chat');
                    const data = await response.json();
                    
                    if (data.success) {
                        showNotification('История чата очищена', 'success');
                        setTimeout(() => {
                            location.reload();
                        }, 1000);
                    } else {
                        showNotification(data.error || 'Ошибка очистки', 'error');
                    }
                } catch (error) {
                    showNotification('Ошибка соединения', 'error');
                }
            }
            
            function toggleTheme() {
                document.body.style.filter = document.body.style.filter ? '' : 'invert(1) hue-rotate(180deg)';
            }
        </script>
    </body>
    </html>
    '''
    return admin_html

@app.route('/logout')
def logout():
    if 'user' in session:
        messages.append(f'Система: {session["user"]} вышел из чата')
        save_messages(messages)
        session.pop('user')
    return redirect('/')

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 УМНЫЙ ЧАТ ЗАПУЩЕН!")
    print("📍 http://localhost:5000")
    print("🔐 Логин: admin")
    print("🔐 Пароль: admin123")
    print("👑 Админ-панель с управлением пользователями")
    print("🔄 Автообновление чата включено")
    print("🎨 Тёмная тема активирована")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)