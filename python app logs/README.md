<<<<<<< HEAD
Aqui nesse diretório, estão alguns projetos de exemplos bem úteis para observabilidade com Datadog.
=======
# Aplicação Python com Flask, Docker e Datadog

Esta é uma aplicação de demonstração simples em Python (Flask) configurada para rodar em Docker com Docker Compose e integrada com o Datadog para envio de logs e traces (APM).

## Pré-requisitos

Você precisará ter instalado em sua máquina:

1.  **Docker**
2.  **Docker Compose**

## Configuração

O arquivo `docker-compose.yml` já está configurado com a sua chave de API do Datadog (`e4e6c70113469277179a34c890af88d3`) e o nome do serviço (`log_traces_giorgio`).

## Como Executar

1.  **Navegue** até o diretório do projeto:
    \`\`\`bash
    cd log_traces_giorgio
    \`\`\`

2.  **Suba** a aplicação e o Datadog Agent usando o Docker Compose:
    \`\`\`bash
    docker compose up --build -d
    \`\`\`

    Isso irá:
    *   Construir a imagem Docker da aplicação.
    *   Iniciar o container da aplicação (`app`) e o container do Datadog Agent (`datadog-agent`).

3.  **Acesse** a aplicação no seu navegador:
    [http://localhost:5000](http://localhost:5000)

## Como Testar e Validar a Integração

1.  **Interaja com a Aplicação:**
    *   Clique nos botões "Requisição de Sucesso", "Requisição com Erro" e "Ação Desconhecida".
    *   Cada clique irá gerar uma requisição HTTP para o backend, que por sua vez gera logs e traces.

2.  **Valide os Traces (APM):**
    *   Acesse o painel de APM (Application Performance Monitoring) no Datadog.
    *   Procure pelo serviço chamado **`log_traces_giorgio`**.
    *   Você deverá ver os traces das requisições que você fez, incluindo os spans do Flask e do Gunicorn.

3.  **Valide os Logs:**
    *   Acesse o painel de Logs no Datadog.
    *   Procure por logs com o serviço **`log_traces_giorgio`**.
    *   Os logs gerados pela aplicação (INFO, ERROR, WARNING) deverão aparecer com o nível de severidade correto, pois agora estão em formato JSON, e estarão automaticamente correlacionados com os traces (graças à variável de ambiente `DD_LOGS_INJECTION=true` e ao Agent).

4.  **Para Parar a Aplicação:**
    \`\`\`bash
    docker compose down
    \`\`\`

## Estrutura do Projeto

\`\`\`
log_traces_giorgio/
├── app.py              # Aplicação Flask com rotas e logs
├── wsgi.py             # Ponto de entrada para Gunicorn e inicialização do ddtrace
├── requirements.txt    # Dependências Python (Flask, Gunicorn, ddtrace, python-json-logger)
├── Dockerfile          # Instruções para construir a imagem Docker da aplicação
├── docker-compose.yml  # Configuração para rodar a aplicação e o Datadog Agent
├── README.md           # Este arquivo
└── templates/
    └── index.html      # Frontend HTML simples com JavaScript para as requisições
\`\`\`
>>>>>>> 5a637aa (Primeiro commit - adiciona python app logs)
