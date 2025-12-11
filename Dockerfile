FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generar archivos gRPC
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ecommerce.proto

EXPOSE 50051

# IMPORTANTE: Ejecutamos app.py, no grpc_server.py
CMD ["python", "app.py"]