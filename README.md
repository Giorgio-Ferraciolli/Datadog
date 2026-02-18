# Projetos usando Datadog
# Datadog + Oracle XE Monitoring Lab 

Este projeto é um laboratório simples para monitorar um banco de dados Oracle XE usando o Datadog Agent em containers Docker.

O objetivo é demonstrar a configuração do Database Monitoring (DBM) do Datadog com Oracle em um ambiente local.

---

## 📦 Tecnologias utilizadas

* Docker
* Docker Compose
* Oracle XE 21c
* Datadog Agent
* Database Monitoring (DBM)

---

## 📁 Estrutura do projeto

```
Datadog/
│
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
│
├── datadog/
│   ├── datadog.yaml
│   └── conf.d/
│       └── oracle.d/
│           └── conf.yaml
│
└── oracle/
    └── init/
        └── create_datadog_user.sql
```

---

## ⚙️ Configuração

### 1. Clone o repositório

```
git clone https://github.com/Giorgio-Ferraciolli/Datadog.git
cd Datadog
```

---

### 2. Configure o arquivo `.env`

Edite o arquivo `.env` e informe sua API Key do Datadog:

```
DATADOG_API_KEY=sua_api_key
DATADOG_SITE=datadoghq.com

ORACLE_HOST=oracle-xe
ORACLE_PORT=1521
ORACLE_SERVICE=XEPDB1
ORACLE_USER=datadog
ORACLE_PASSWORD=datadog

ENVIRONMENT=lab
PROJECT=oracle-datadog
```

---

## ▶️ Como executar

Subir os containers:

```
docker compose up -d
```

Verificar status:

```
docker compose ps
```

Ver logs do Datadog Agent:

```
docker compose logs -f datadog-agent
```

---

## 📊 Visualizar no Datadog

No portal do Datadog, acesse:

```
Database Monitoring → Databases
```

Você verá o banco Oracle sendo monitorado.

---

## 🎯 Objetivo do projeto

Este projeto demonstra:

* Integração do Datadog com Oracle
* Uso do Docker para ambiente isolado
* Configuração de Database Monitoring
* Estrutura organizada para ambiente DevOps

---

## 👤 Autor

Giorgio Ferraciolli

---

## 📄 Licença

Uso livre para fins de estudo e laboratório.
