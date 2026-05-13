# 📚 Biblioteca Pessoal — instrumentada com Datadog APM

App de exemplo em **Ruby + Sinatra** com **PostgreSQL**, frontend em ERB,
e **Datadog APM** já configurado (gem `datadog` v2.x).

Tema: tracker de leitura. Cadastra livros, registra sessões (páginas lidas por dia),
acompanha progresso e vê estatísticas.

## Rodar

1. Copia o `.env.example` pra `.env` e coloca sua API key:

   ```bash
   cp .env.example .env
   # edita .env e coloca DD_API_KEY e DD_SITE
   ```

2. Sobe tudo:

   ```bash
   docker compose up --build
   ```

App: <http://localhost:4567>

Para resetar o banco:

```bash
docker compose down -v
docker compose up --build
```

## Stack

| Camada     | Tecnologia                                 |
|------------|--------------------------------------------|
| Web        | Sinatra 4 + Puma                           |
| ORM        | Sequel                                     |
| Banco      | PostgreSQL 16                              |
| APM        | gem `datadog` 2.x + Datadog Agent (no compose) |
| Frontend   | ERB + CSS puro                             |

## Datadog APM

### Setup

A instrumentação acontece em `lib/tracing.rb`:

```ruby
require 'datadog'

Datadog.configure do |c|
  c.service = 'biblioteca-pessoal'
  c.env     = ENV.fetch('DD_ENV', 'development')
  c.version = '1.0.0'

  c.tracing.instrument :sinatra
  c.tracing.instrument :rack
  c.tracing.instrument :pg, service_name: 'biblioteca-pg'
end
```

O arquivo é carregado **depois** das libs (sinatra/pg/sequel) em `app.rb` —
isso é importante para o `Datadog.configure` detectá-las.

### Auto-instrumentação

- **Rack** — cria o span raiz de cada request
- **Sinatra** — adiciona a rota como resource (`GET /books/:id`)
- **PG** — cria um span pra cada query SQL, com a query como resource

### Spans manuais

Em `app.rb`, cada operação de negócio cria um span próprio com tags
customizadas. Exemplo na rota `/stats`:

```
rack.request
└─ sinatra.request   (resource: GET /stats)
   └─ stats.compute
      ├─ stats.totals
      │  └─ pg.query (COUNT, COUNT, COUNT, ...)
      ├─ stats.by_genre
      │  └─ pg.query
      └─ stats.last_7_days
         └─ pg.query
```

### Onde os traces aparecem no Datadog

- **APM > Services**: o serviço `biblioteca-pessoal` aparece após o primeiro request
- **APM > Traces**: traces individuais com a árvore completa
- **APM > Service Map**: relação entre `biblioteca-pessoal` e `biblioteca-pg`

### Tags úteis pra filtrar

- `service:biblioteca-pessoal`
- `env:development`
- `version:1.0.0`
- `team:observability-study`
- Tags por span: `book.id`, `book.title`, `filter.status`, `db.rows_returned`, etc.

### Debugando

Se traces não aparecerem, ativa o modo debug no `docker-compose.yml`:

```yaml
DD_TRACE_DEBUG: "true"
```

E olha os logs:
```bash
docker compose logs -f app | grep -i datadog
docker compose logs -f datadog | grep -i trace
```

Também tem o status do agent:
```bash
docker compose exec datadog agent status
```

## Estrutura

```
.
├── app.rb                  # rotas Sinatra (com spans manuais)
├── config.ru
├── Dockerfile
├── docker-compose.yml      # inclui datadog-agent
├── .env.example            # template de configuração
├── Gemfile
├── bin/start
├── lib/
│   ├── tracing.rb          # Datadog.configure
│   ├── db.rb
│   └── models/
├── db/
├── views/
└── public/styles.css
```

## Rotas

| Método | Path                       | O que faz                       |
|--------|----------------------------|---------------------------------|
| GET    | `/`                        | Lista livros (com filtro)       |
| GET    | `/books/new`               | Form de novo livro              |
| POST   | `/books`                   | Cria livro                      |
| GET    | `/books/:id`               | Detalhe + histórico de sessões  |
| POST   | `/books/:id/sessions`      | Registra sessão de leitura      |
| POST   | `/books/:id/delete`        | Remove livro                    |
| GET    | `/stats`                   | Estatísticas (mais spans)       |
| GET    | `/health`                  | Healthcheck                     |
