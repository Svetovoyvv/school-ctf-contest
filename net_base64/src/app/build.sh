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

echo "Проверка сгенерированного кода..."
echo "Строка с флагом:"
grep "storedFlag" Program.cs | head -n 1

echo "Компиляция приложения для Windows (.NET Framework для dnSpy)..."
# Собираем для .NET Framework - создается один exe с IL кодом
# Такой файл отлично открывается в dnSpy
dotnet build -c Release -o /output

echo "Сборка завершена успешно!"

if [ -d "/app/output" ]; then
    echo "Копирование exe файла в /app/output..."
    
    if [ -f "/output/PasswordChecker.exe" ]; then
        cp /output/PasswordChecker.exe /app/output/
        
        echo "Приложение PasswordChecker.exe скопировано в /app/output"
        ls -lh /app/output/PasswordChecker.exe
        
        echo ""
        echo "✅ Сборка завершена успешно!"
        echo "Флаг можно найти, открыв PasswordChecker.exe в dnSpy"
    else
        echo "Ошибка: PasswordChecker.exe не найден в /output"
        ls -lh /output/
        exit 1
    fi
fi
