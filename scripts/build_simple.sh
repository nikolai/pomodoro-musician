#!/bin/bash

# Простой скрипт для создания .app для macOS

echo "🔨 Создание исполняемого файла Pomodoro Timer..."

# Установка PyInstaller
echo "📦 Установка PyInstaller..."
/usr/bin/python3 -m pip install --user pyinstaller

# Создание .app файла (простая версия)
echo "🚀 Сборка приложения..."
/usr/bin/python3 -m PyInstaller \
    --name "PomodoroTimer" \
    --windowed \
    --onefile \
    --add-data "alarm.wav:." \
    --add-data "break_alarm.wav:." \
    pomodoro.py

echo ""
echo "✅ Готово!"
echo "📂 Приложение находится в папке: dist/PomodoroTimer.app"
echo "📱 Вы можете скопировать этот файл на другой Mac и запустить"
echo ""
echo "💡 Совет: Сожмите .app в .zip для передачи"

