# Use uma imagem base Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Comando para rodar a aplicação com Gunicorn
# O ddtrace será ativado pelas variáveis de ambiente no docker-compose
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
