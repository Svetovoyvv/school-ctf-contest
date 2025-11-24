#!/bin/bash

set -e
PASSWORD="${FLAG}"
if [ -z "$PASSWORD" ]; then
    echo "Ошибка: переменная окружения PASSWORD не установлена"
    exit 1
fi

echo "Кодирование пароля в base64..."
# Используем openssl для кодирования base64
BASE64_PASSWORD=$(echo -n "$PASSWORD" | openssl base64 | tr -d '\n')
EXPECTED_FLAG_STRING="Password is ${BASE64_PASSWORD}"
echo "Ожидаемая строка в exe: ${EXPECTED_FLAG_STRING}"

echo "Генерация Program.cs из шаблона..."
sed "s|{{BASE64_PASSWORD}}|${BASE64_PASSWORD}|g" Program.cs.template > Program.cs

echo "Компиляция приложения для Windows (single-file)..."
# Публикуем как single-file. Использование UTF-8 литералов (u8) в коде гарантирует,
# что строка попадет в бинарник в ASCII-совместимом виде.
dotnet publish -c Debug -r win-x64 \
  --self-contained true \
  -p:PublishSingleFile=true \
  -p:PublishTrimmed=false \
  -p:PublishReadyToRun=false \
  -p:IncludeNativeLibrariesForSelfExtract=true \
  -p:EnableCompressionInSingleFile=false \
  -p:DebugType=portable \
  -p:DebugSymbols=true \
  -p:IncludeSymbols=true \
  -p:Optimize=false \
  -o /output

echo "Сборка завершена успешно!"

if [ -d "/app/output" ]; then
    echo "Копирование exe файла в /app/output..."
    
    if [ -f "/output/PasswordChecker.exe" ]; then
        cp /output/PasswordChecker.exe /app/output/
        echo "Приложение PasswordChecker.exe скопировано в /app/output"
        ls -lh /app/output/PasswordChecker.exe
        
        echo ""
        echo "=== ПРОВЕРКА CTF ЗАДАЧИ ==="
        echo "Поиск флага через grep в бинарном файле..."
        
        # Ищем точную строку флага. grep -a (treat binary as text) обязателен.
        # -F (fixed string) для скорости и точности.
        if grep -aF "${EXPECTED_FLAG_STRING}" /app/output/PasswordChecker.exe > /dev/null; then
            echo "✅ УСПЕХ: Флаг найден в файле с помощью grep!"
            echo "Найденная строка:"
            grep -aF "${EXPECTED_FLAG_STRING}" /app/output/PasswordChecker.exe
        else
            echo "❌ ОШИБКА: Флаг НЕ найден в файле через grep."
            echo "Попробуем найти хотя бы часть 'Flag is'..."
            grep -a "Flag is" /app-output/PasswordChecker.exe | head -n 3
            exit 1
        fi
    else
        echo "Ошибка: PasswordChecker.exe не найден в /output"
        exit 1
    fi
fi
