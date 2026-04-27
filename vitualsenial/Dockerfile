FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instalar librerías de Python directamente
RUN pip install --no-cache-dir pyserial opencv-python-headless

# Copiar el código al contenedor
COPY . .

CMD ["python", "ledOn.py"]
