# Используем базовый образ Python
FROM python:3.12-slim

# Установка необходимых пакетов
RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app/backend_folder

# Копируем файлы микросервиса
COPY ./backend_folder/ .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Открытие порта
EXPOSE 8000

# Запуск сервиса
CMD ["uvicorn", "main_back:app", "--host", "0.0.0.0", "--port", "8000"]
