# Datadog MySQL Monitoring (Docker)

Projeto simples para monitorar um MySQL rodando em Docker usando o Datadog com Database Monitoring (DBM) ativado.

## Objetivo

Subir um container MySQL e coletar métricas no Datadog, como:

* Queries por segundo
* Performance das queries
* Conexões
* Uso geral do banco

## Tecnologias usadas

* Docker
* Docker Compose
* MySQL
* Datadog Agent
* Datadog DBM

## Estrutura

```
.
├── docker-compose.yml
├── .env
└── init.sql
```

## Configuração

1. Configure o arquivo `.env`:

```
DATADOG_API_KEY=sua_api_key
DATADOG_SITE=datadoghq.com
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=datadog
```

2. Suba os containers:

```
docker compose up -d
```

## Verificação

No Datadog, vá em:

```
Metrics → mysql.performance.queries
```

Filtre por:

```
database_hostname:mysql-db
```

## Resultado

O Datadog irá coletar automaticamente métricas do MySQL rodando no Docker.

---

Projeto criado para fins de estudo e testes com Datadog DBM.
