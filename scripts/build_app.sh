#!/bin/bash

# Скрипт для создания .app для macOS

echo "🔨 Создание исполняемого файла Pomodoro Timer..."

# Установка PyInstaller если нужно
echo "📦 Проверка PyInstaller..."
/usr/bin/python3 -m pip install --user pyinstaller

# Создание .app файла
echo "🚀 Сборка приложения..."
/usr/bin/python3 -m PyInstaller \
    --name "Pomodoro Timer" \
    --windowed \
    --onefile \
    --icon=icon.icns \
    --add-data "alarm.wav:." \
    --add-data "break_alarm.wav:." \
    --osx-bundle-identifier "com.pomodoro.timer" \
    pomodoro.py

echo "✅ Готово! Приложение находится в папке dist/"
echo "📱 Вы можете скопировать 'Pomodoro Timer.app' на другой Mac"

