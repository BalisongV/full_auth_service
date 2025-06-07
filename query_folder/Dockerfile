FROM python:3.12-slim

# Установка GCC для сборки зависимостей
RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app/query_folder

# Копируем код
COPY ./query_folder/  .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Запуск сервиса
CMD ["uvicorn", "main_query:app", "--host", "0.0.0.0", "--port", "8003"]
