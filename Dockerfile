# Usar uma imagem base do Ubuntu
FROM ubuntu:20.04

# Definir o diretório de trabalho
WORKDIR /app

# Instalar dependências e o curl
RUN apt-get update && apt-get install -y \
  curl \
  python3 \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instalar as dependências do projeto
RUN pip3 install --no-cache-dir -r requirements.txt

# Instalar flask-openapi3 com Swagger UI
RUN pip3 install -U flask-openapi3[swagger]

# Copiar o restante do código do projeto para o diretório de trabalho
COPY . .

# Documentar as portas que serão utilizadas
EXPOSE 5000

# Definir o comando para rodar o app (isso será sobrescrito pelo docker-compose)
#CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
CMD ["python3", "app.py"]
