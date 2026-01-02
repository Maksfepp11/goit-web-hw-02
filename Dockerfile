# Використовуємо Python 3.13
FROM python:3.13-slim

# Робоча директорія
WORKDIR /app

# Копіюємо весь проект у контейнер
COPY . /app

# Відключаємо буферизацію виводу Python
ENV PYTHONUNBUFFERED=1

# Команда запуску застосунку
CMD ["python", "main.py"]
