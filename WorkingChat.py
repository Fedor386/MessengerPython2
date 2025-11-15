from flask import Flask, request, session, redirect
import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'secure-chat-key-2024'

# Файлы для хранения данных
USERS_FILE = 'chat_users.json'
ADMINS_FILE = 'admin_users.txt'

def load_users():
    """Загружаем пользователей из файла"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Сохраняем пользователей в файл"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_admins():
    """Загружаем список администраторов"""
    admins = set()
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    username = line.strip()
                    if username:
                        admins.add(username)
        except:
            pass
    return admins

def save_admins(admins):
    """Сохраняем список администраторов"""
    with open(ADMINS_FILE, 'w', encoding='utf-8') as f:
        for username in admins:
            f.write(username + '\n')

def is_admin(username):
    """Проверяем является ли пользователь администратором"""
    admins = load_admins()
    return username in admins

# Загружаем пользователей
users = load_users()
if not users:
    # Создаем администратора по умолчанию
    users = {
        'admin': {
            'password': 'A1D2M3I4N5',
            'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    }
    save_users(users)
    
    # Добавляем admin в список администраторов
    admins = load_admins()
    admins.add('admin')
    save_admins(admins)

# Хранилище сообщений
messages = []

@app.route('/')
def home():
    current_user = session.get('username')
    user_count = len(users)
    message_count = len(messages)
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Безопасный чат</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .btn {{
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 5px;
        }}
        .btn-success {{ background: #28a745; }}
        .btn-warning {{ background: #ffc107; color: black; }}
        .stats {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .user-info {{
            background: #d4edda;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .admin-note {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #ffc107;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Безопасный чат</h1>
        
        {'<div class="user-info">✅ Вы вошли как: <strong>' + current_user + '</strong>' + (' <span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">ADMIN</span>' if is_admin(current_user) else '') + '</div>' if current_user else ''}
        
        <div class="stats">
            <p><strong>📊 Статистика:</strong></p>
            <p>• Пользователей: <strong>{user_count}</strong></p>
            <p>• Администраторов: <strong>{len(load_admins())}</strong></p>
            <p>• Сообщений: <strong>{message_count}</strong></p>
        </div>
        
        <div style="text-align: center;">
            {'<a href="/chat" class="btn">💬 Перейти в чат</a>' if current_user else '<a href="/login" class="btn">🔐 Войти в чат</a>'}
            <a href="/register" class="btn btn-success">👤 Регистрация</a>
            {'<a href="/users" class="btn btn-warning">👥 Управление</a>' if current_user and is_admin(current_user) else ''}
        </div>
        
        <div class="admin-note">
            <strong>ℹ️ Важная информация:</strong><br>
            • При регистрации создаются только обычные пользователи<br>
            • Права администратора выдаются через консоль<br>
            • Администраторы могут управлять пользователями
        </div>
    </div>
</body>
</html>
'''

@app.route('/login')
def login_page():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Вход</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .login-box {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 300px;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 8px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 10px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .links {
            text-align: center;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2 style="text-align: center;">🔐 Вход</h2>
        <form action="/do_login" method="POST">
            <input type="text" name="username" placeholder="Логин" required>
            <input type="password" name="password" placeholder="Пароль" required>
            <button>Войти</button>
        </form>
        <div class="links">
            <a href="/register">Создать аккаунт</a> | 
            <a href="/">На главную</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/do_login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username]['password'] == password:
        session['username'] = username
        
        # Добавляем системное сообщение
        messages.append({
            'type': 'system',
            'content': f'🟢 {username} вошел в чат',
            'time': datetime.datetime.now().strftime("%H:%M")
        })
        
        return redirect('/chat')
    else:
        return '''
        <div style="text-align: center; padding: 50px;">
            <h3 style="color: red;">❌ Ошибка входа</h3>
            <p>Неверный логин или пароль</p>
            <a href="/login">← Назад</a>
        </div>
        '''

@app.route('/register')
def register_page():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Регистрация</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .register-box {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 320px;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 8px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 10px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .message {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info-box {
            background: #e7f3ff;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="register-box">
        <h2 style="text-align: center;">👤 Регистрация</h2>
        
        <div class="info-box">
            <strong>⚠️ Внимание:</strong><br>
            При регистрации создается только обычный пользователь.<br>
            Права администратора выдаются отдельно.
        </div>
        
        <div id="message"></div>
        
        <form onsubmit="registerUser(event)">
            <input type="text" id="username" placeholder="Логин (мин. 3 символа)" required>
            <input type="password" id="password" placeholder="Пароль (мин. 4 символа)" required>
            <input type="password" id="confirm_password" placeholder="Повторите пароль" required>
            <button type="submit">✅ Зарегистрировать</button>
        </form>
        
        <div style="text-align: center; margin-top: 15px;">
            <a href="/login">← Войти</a> | 
            <a href="/">На главную</a>
        </div>
    </div>

    <script>
        async function registerUser(event) {
            event.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (username.length < 3) {
                showMessage('Логин должен быть не менее 3 символов', 'error');
                return;
            }
            
            if (password.length < 4) {
                showMessage('Пароль должен быть не менее 4 символов', 'error');
                return;
            }
            
            if (password !== confirmPassword) {
                showMessage('Пароли не совпадают', 'error');
                return;
            }
            
            const response = await fetch('/do_register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            });
            
            if (response.ok) {
                showMessage(`✅ Пользователь ${username} успешно создан!<br><small>Теперь вы можете войти в систему</small>`, 'success');
                document.querySelector('form').reset();
            } else {
                const error = await response.text();
                showMessage('❌ ' + error, 'error');
            }
        }
        
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = text;
        }
    </script>
</body>
</html>
'''

@app.route('/do_register', methods=['POST'])
def do_register():
    username = request.form['username'].strip()
    password = request.form['password']
    
    if len(username) < 3:
        return "Логин слишком короткий", 400
    
    if username in users:
        return "Пользователь уже существует", 400
    
    if len(password) < 4:
        return "Пароль слишком короткий", 400
    
    # Сохраняем пользователя (только как обычного пользователя)
    users[username] = {
        'password': password,
        'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    save_users(users)
    
    return "OK"

@app.route('/users')
def users_page():
    current_user = session.get('username')
    if not current_user or not is_admin(current_user):
        return '''
        <div style="text-align: center; padding: 50px;">
            <h3 style="color: red;">❌ Доступ запрещен</h3>
            <p>Только администраторы могут просматривать эту страницу</p>
            <a href="/">← На главную</a>
        </div>
        ''', 403
    
    admins = load_admins()
    
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Управление пользователями</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
        }}
        .user-item {{
            padding: 12px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .admin-badge {{
            background: #dc3545;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
            margin-left: 10px;
        }}
        .btn {{
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            font-size: 12px;
            margin-left: 5px;
        }}
        .btn-danger {{ background: #dc3545; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-warning {{ background: #ffc107; color: black; }}
        .admin-actions {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>👥 Управление пользователями</h1>
        
        <div class="admin-actions">
            <strong>Административные действия:</strong><br>
            <button class="btn btn-success" onclick="showAddAdminForm()">➕ Назначить администратора</button>
            <button class="btn btn-warning" onclick="showRemoveAdminForm()">➖ Снять администратора</button>
        </div>
        
        <p><strong>Всего пользователей:</strong> {len(users)} | <strong>Администраторов:</strong> {len(admins)}</p>
        
        <div id="usersList">
'''
    
    # Сортируем пользователей по имени
    sorted_users = sorted(users.items())
    
    for username, user_data in sorted_users:
        is_admin_user = username in admins
        created = user_data.get('created', 'Неизвестно')
        admin_badge = '<span class="admin-badge">ADMIN</span>' if is_admin_user else ''
        
        delete_button = f'<button class="btn btn-danger" onclick="deleteUser(\'{username}\')">🗑️ Удалить</button>'
        if username == current_user:
            delete_button = '<button class="btn" disabled>Текущий пользователь</button>'
        
        html += f'''
            <div class="user-item">
                <div>
                    <strong>{username}</strong> {admin_badge}
                    <br><small>Создан: {created}</small>
                </div>
                <div>
                    {delete_button}
                </div>
            </div>
        '''
    
    html += '''
        </div>
        
        <div style="margin-top: 20px;">
            <a href="/" class="btn" style="background: #007bff;">← На главную</a>
            <a href="/chat" class="btn" style="background: #28a745;">💬 В чат</a>
        </div>
    </div>

    <script>
        function deleteUser(username) {
            if (!confirm('Удалить пользователя ' + username + '?')) {
                return;
            }
            
            fetch('/delete_user?username=' + encodeURIComponent(username))
                .then(response => {
                    if (response.ok) {
                        alert('Пользователь удален');
                        location.reload();
                    } else {
                        alert('Ошибка при удалении');
                    }
                });
        }
        
        function showAddAdminForm() {
            const username = prompt('Введите логин пользователя для назначения администратором:');
            if (username) {
                fetch('/add_admin?username=' + encodeURIComponent(username))
                    .then(response => {
                        if (response.ok) {
                            alert('Пользователь ' + username + ' назначен администратором');
                            location.reload();
                        } else {
                            response.text().then(error => alert('Ошибка: ' + error));
                        }
                    });
            }
        }
        
        function showRemoveAdminForm() {
            const username = prompt('Введите логин администратора для снятия прав:');
            if (username) {
                fetch('/remove_admin?username=' + encodeURIComponent(username))
                    .then(response => {
                        if (response.ok) {
                            alert('Права администратора сняты с пользователя ' + username);
                            location.reload();
                        } else {
                            response.text().then(error => alert('Ошибка: ' + error));
                        }
                    });
            }
        }
    </script>
</body>
</html>
'''
    return html

@app.route('/delete_user')
def delete_user():
    current_user = session.get('username')
    if not current_user or not is_admin(current_user):
        return "Доступ запрещен", 403
    
    username = request.args.get('username')
    
    if username == current_user:
        return "Нельзя удалить себя", 400
    
    if username in users:
        del users[username]
        save_users(users)
        
        # Удаляем из администраторов если был
        admins = load_admins()
        if username in admins:
            admins.remove(username)
            save_admins(admins)
            
        return "OK"
    else:
        return "Пользователь не найден", 404

@app.route('/add_admin')
def add_admin():
    current_user = session.get('username')
    if not current_user or not is_admin(current_user):
        return "Доступ запрещен", 403
    
    username = request.args.get('username')
    
    if username not in users:
        return "Пользователь не найден", 404
    
    admins = load_admins()
    admins.add(username)
    save_admins(admins)
    
    return "OK"

@app.route('/remove_admin')
def remove_admin():
    current_user = session.get('username')
    if not current_user or not is_admin(current_user):
        return "Доступ запрещен", 403
    
    username = request.args.get('username')
    
    if username == current_user:
        return "Нельзя снять права с себя", 400
    
    admins = load_admins()
    if username in admins:
        admins.remove(username)
        save_admins(admins)
        return "OK"
    else:
        return "Пользователь не является администратором", 400

# Остальные маршруты (chat, get_messages, send_message, logout) остаются аналогичными предыдущему примеру

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    user_is_admin = is_admin(username)
    
    admin_link = ''
    if user_is_admin:
        admin_link = '<a href="/users" style="color: white; margin-left: 15px; background: #28a745; padding: 8px 15px; border-radius: 5px; text-decoration: none;">👥 Управление</a>'
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>Чат • {username}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #f5f5f5;
            font-family: Arial, sans-serif;
        }}
        .header {{
            background: #007bff;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .chat-container {{
            max-width: 800px;
            margin: 20px auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
        }}
        .messages {{
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 15px;
            background: #fafafa;
        }}
        .message {{
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
        }}
        .my-message {{
            background: #e3f2fd;
            margin-left: 50px;
        }}
        .other-message {{
            background: #f1f1f1;
            margin-right: 50px;
        }}
        .system-message {{
            background: #fff3cd;
            text-align: center;
            font-style: italic;
        }}
        .input-group {{
            display: flex;
            gap: 10px;
        }}
        input {{
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        button {{
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h2>💬 Чат</h2>
        <div>
            <span>Вы: <strong>{username}</strong>{' <span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">ADMIN</span>' if user_is_admin else ''}</span>
            {admin_link}
            <a href="/logout" style="color: white; margin-left: 15px; background: #dc3545; padding: 8px 15px; border-radius: 5px; text-decoration: none;">Выйти</a>
        </div>
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages">
            {get_messages_html(username)}
        </div>
        
        <div class="input-group">
            <input type="text" id="messageInput" placeholder="Введите сообщение..." onkeypress="if(event.key=='Enter') sendMessage()">
            <button onclick="sendMessage()">Отправить</button>
        </div>
    </div>

    <script>
        function sendMessage() {{
            var input = document.getElementById('messageInput');
            var message = input.value.trim();
            
            if (message) {{
                fetch('/send_message', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                    body: 'message=' + encodeURIComponent(message)
                }}).then(function() {{
                    input.value = '';
                    loadMessages();
                }});
            }}
        }}
        
        function loadMessages() {{
            fetch('/get_messages')
                .then(response => response.text())
                .then(html => {{
                    document.getElementById('messages').innerHTML = html;
                    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                }});
        }}
        
        setInterval(loadMessages, 2000);
        document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
    </script>
</body>
</html>
'''

def get_messages_html(username):
    html = ''
    for msg in messages:
        if msg['type'] == 'system':
            html += f'<div class="system-message">{msg["content"]}</div>'
        else:
            if msg['user'] == username:
                html += f'<div class="message my-message"><strong>Вы:</strong> {msg["content"]}</div>'
            else:
                html += f'<div class="message other-message"><strong>{msg["user"]}:</strong> {msg["content"]}</div>'
    return html

@app.route('/get_messages')
def get_messages():
    username = session.get('username', '')
    return get_messages_html(username)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session:
        return 'Ошибка', 401
    
    username = session['username']
    message = request.form['message']
    
    if message.strip():
        messages.append({
            'user': username,
            'content': message,
            'time': datetime.datetime.now().strftime("%H:%M"),
            'type': 'user'
        })
    
    return 'OK'

@app.route('/logout')
def logout():
    username = session.pop('username', None)
    if username:
        messages.append({
            'type': 'system',
            'content': f'🔴 {username} вышел из чата',
            'time': datetime.datetime.now().strftime("%H:%M")
        })
    return redirect('/')

def admin_console():
    """Консоль для управления администраторами"""
    while True:
        print("\n" + "="*50)
        print("🔧 КОНСОЛЬ УПРАВЛЕНИЯ АДМИНИСТРАТОРАМИ")
        print("="*50)
        print("1 - Список всех пользователей")
        print("2 - Назначить администратора")
        print("3 - Снять администратора") 
        print("4 - Список администраторов")
        print("5 - Выйти")
        
        choice = input("\nВыберите действие: ").strip()
        
        if choice == '1':
            print("\n👥 ВСЕ ПОЛЬЗОВАТЕЛИ:")
            admins = load_admins()
            for username, user_data in sorted(users.items()):
                role = "ADMIN" if username in admins else "USER"
                print(f"  {username} - {role} (создан: {user_data.get('created', 'Неизвестно')})")
                
        elif choice == '2':
            username = input("Введите логин пользователя для назначения администратором: ").strip()
            if username in users:
                admins = load_admins()
                admins.add(username)
                save_admins(admins)
                print(f"✅ Пользователь {username} назначен администратором")
            else:
                print("❌ Пользователь не найден")
                
        elif choice == '3':
            username = input("Введите логин администратора для снятия прав: ").strip()
            admins = load_admins()
            if username in admins:
                if username == 'admin':
                    print("❌ Нельзя снять права с основного администратора")
                else:
                    admins.remove(username)
                    save_admins(admins)
                    print(f"✅ Права администратора сняты с пользователя {username}")
            else:
                print("❌ Пользователь не является администратором")
                
        elif choice == '4':
            admins = load_admins()
            print("\n👑 АДМИНИСТРАТОРЫ:")
            for admin in sorted(admins):
                print(f"  {admin}")
                
        elif choice == '5':
            break
        else:
            print("❌ Неверный выбор")

if __name__ == '__main__':
    # Добавляем приветственное сообщение
    messages.append({
        'type': 'system', 
        'content': '💬 Добро пожаловать в безопасный чат!',
        'time': datetime.datetime.now().strftime("%H:%M")
    })
    
    print("=" * 60)
    print("🚀 БЕЗОПАСНЫЙ ЧАТ ЗАПУЩЕН!")
    print("=" * 60)
    print("🌐 Откройте: http://localhost:5000")
    print("")
    print("🔐 Администратор по умолчанию:")
    print("   Логин: admin")
    print("   Пароль: A1D2M3I4N5")
    print("")
    print("🔧 Управление администраторами через консоль:")
    print("   Запустите команду: admin_console()")
    print("=" * 60)
    
    # Запускаем в отдельном потоке консоль администрирования
    import threading
    console_thread = threading.Thread(target=admin_console, daemon=True)
    console_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=True)