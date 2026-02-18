# Datadog Oracle XE Integration

Este repositório contém a configuração necessária para monitorar um banco Oracle XE usando o Datadog Agent.

## Estrutura

- agent/datadog.yaml → Configuração principal do Datadog Agent
- oracle/conf.d/oracle.d/conf.yaml → Configuração específica da integração Oracle

## Pré-requisitos

- Datadog Agent instalado
- Oracle XE rodando
- Usuário com permissões de monitoramento

## Local padrão no Linux

Os arquivos devem ser copiados para:

/etc/datadog-agent/datadog.yaml
/etc/datadog-agent/conf.d/oracle.d/conf.yaml

## Reiniciar o agent

```bash
sudo systemctl restart datadog-agent
