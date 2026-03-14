FROM python:3.10-slim

# Dependencias del sistema (del packages.txt original)
RUN apt-get update && apt-get install -y \
    libgl1  \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psycopg2-binary

# Copiar código de la aplicación
COPY . .

# Exponer puerto de Streamlit
EXPOSE 8501

# Configuración de Streamlit para producción
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Ejecutar como usuario no root
RUN useradd -m appuser
USER appuser

CMD ["streamlit", "run", "main.py", \
     "--server.headless=true", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]