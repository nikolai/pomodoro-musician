#!/bin/bash

# Улучшенный скрипт для создания .app для macOS
# Этот скрипт создаёт более совместимую версию приложения

echo "🔨 Создание Pomodoro Timer для macOS..."
echo ""

# Очистка предыдущих сборок
if [ -d "build" ]; then
    echo "🧹 Очистка старых файлов сборки..."
    rm -rf build dist *.spec
fi

# Установка PyInstaller
echo "📦 Проверка PyInstaller..."
/usr/bin/python3 -m pip install --user pyinstaller --quiet

# Создание .app файла с улучшенными параметрами
echo "🚀 Сборка приложения..."
/usr/bin/python3 -m PyInstaller \
    --name "PomodoroTimer" \
    --windowed \
    --onedir \
    --clean \
    --noconfirm \
    --add-data "alarm.wav:." \
    --add-data "break_alarm.wav:." \
    --osx-bundle-identifier "com.pomodoro.timer" \
    --hidden-import=pygame \
    pomodoro.py

echo ""
echo "✅ Сборка завершена!"
echo ""
echo "📂 Приложение: dist/PomodoroTimer.app"
echo ""

# Создание ZIP
echo "📦 Создание ZIP-архива..."
cd dist
zip -r -q PomodoroTimer.zip PomodoroTimer.app
cd ..

# Копирование инструкции
cp INSTALL_INSTRUCTIONS.md dist/

echo "✅ ZIP создан: dist/PomodoroTimer.zip"
echo "📄 Инструкция добавлена: dist/INSTALL_INSTRUCTIONS.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 ВСЁ ГОТОВО!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📤 Для передачи на другой Mac:"
echo "   1. Отправьте файл: dist/PomodoroTimer.zip"
echo "   2. Отправьте инструкцию: dist/INSTALL_INSTRUCTIONS.md"
echo ""
echo "💡 Важно! Получатель должен:"
echo "   - Распаковать ZIP"
echo "   - Открыть через ПРАВЫЙ КЛИК → Открыть"
echo "   - Или выполнить: xattr -cr PomodoroTimer.app"
echo ""
echo "📝 Подробная инструкция в INSTALL_INSTRUCTIONS.md"
echo ""


