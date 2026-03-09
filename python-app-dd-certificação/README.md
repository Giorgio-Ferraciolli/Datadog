# Aplicação em Python (FastAPI) para estudos preparatórios para a certificação Datadog Fundamentals

## Simulador de Respostas HTTP

Este projeto simula diferentes respostas HTTP (200, 404, 500) para testes.

## Como Rodar

1.  Certifique-se de ter Docker e Docker Compose instalados.
2.  Navegue até a pasta da aplicação
3.  Execute:
    ```bash
    docker compose up --build
    ```
    Isso irá construir a imagem Docker e iniciar o contêiner. O volume de montagem foi removido para garantir que as dependências sejam corretamente instaladas dentro do contêiner.
4.  Acesse `http://localhost:8000` no seu navegador.
