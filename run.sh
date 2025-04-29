#!/bin/bash

echo "🔧 Установка виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Установка зависимостей..."
pip install -r requirements.txt

echo "🚀 Бот запущен брат"
sleep 10
python bot.py
