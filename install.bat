@echo off
chcp 65001 >nul
echo ===============================
echo  ЗАПУСК БЕЗОПАСНОГО ЧАТА
echo ===============================
echo.

echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не найден!
    echo Установите Python с python.org
    pause
    exit /b 1
)

echo ✅ Python обнаружен
echo.

echo Установка Flask и Bcrypt...
echo.
pip install bcrypt
pip install flask

echo ✅ Все готово!
echo.
echo Нажмите любую клавишу для того чтобы выйти
pause >nul