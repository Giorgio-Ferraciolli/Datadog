# Guia de Integração Datadog (Kubernetes) com RabbitMQ (VM Externa) via Prometheus

Este guia detalha o processo de configuração do monitoramento de uma instância do **RabbitMQ** rodando em uma **Máquina Virtual (VM)** externa, utilizando o **Datadog Agent** implantado em um cluster **Kubernetes**.

A solução se baseia no uso do **Plugin Prometheus** do RabbitMQ para expor as métricas e do mecanismo de **Cluster Checks** do Datadog, que permite que o Datadog Cluster Agent execute verificações de monitoramento de forma centralizada para serviços externos ao cluster [1].

---

## 1. Pré-requisitos no RabbitMQ (VM Externa)

Para que o Datadog possa coletar métricas do RabbitMQ via Prometheus, o plugin correspondente deve estar habilitado e a porta de exposição deve estar acessível.

### 1.1. Habilitar o Plugin Prometheus

O Datadog Agent utilizará o endpoint de métricas do Prometheus. O plugin `rabbitmq_prometheus` é o responsável por expor essas métricas.

```bash
# Habilitar o plugin do Prometheus
sudo rabbitmq-plugins enable rabbitmq_prometheus
```

**Nota:** A partir do RabbitMQ v3.8, este plugin é habilitado por padrão [2].

### 1.2. Configuração de Rede

É fundamental garantir que o Datadog Agent, rodando no Kubernetes, consiga se comunicar com a VM do RabbitMQ na porta correta.

1.  **Endereço IP:** Obtenha o endereço IP privado da VM do RabbitMQ (ex: `192.168.1.10`).
2.  **Porta:** A porta padrão para o endpoint de métricas do Prometheus é **15692** e o caminho é `/metrics` [3].
3.  **Regras de Firewall/Security Group:** Certifique-se de que o firewall da VM e quaisquer *Security Groups* ou *Network Policies* na rede permitam o tráfego de entrada na porta **15692** a partir dos IPs de saída do seu cluster Kubernetes.

---

## 2. Configuração do Datadog Agent (Kubernetes)

A configuração será aplicada ao **Datadog Cluster Agent** usando o mecanismo de **Cluster Checks** e uma configuração estática, utilizando a seção `prometheus_plugin` da integração RabbitMQ.

### 2.1. Habilitar Cluster Checks

Se ainda não estiver habilitado, o *Cluster Check Dispatching* deve ser ativado no Datadog Cluster Agent. Se você estiver usando o Datadog Operator, a configuração é feita no `DatadogAgent` Custom Resource Definition (CRD):

```yaml
apiVersion: datadoghq.com/v2alpha1
kind: DatadogAgent
metadata:
  name: datadog
spec:
  features:
    clusterChecks:
      enabled: true # Deve ser 'true'
# ...
```

### 2.2. Criar o Arquivo de Configuração do RabbitMQ (via Prometheus)

Crie um arquivo de configuração estática para a integração do RabbitMQ. Este arquivo deve ser nomeado `rabbitmq.yaml` e deve incluir `cluster_check: true` para garantir que a verificação seja executada apenas uma vez pelo Cluster Agent [1].

**`/home/ubuntu/rabbitmq.yaml`**
```yaml
cluster_check: true
init_config:
  # Opcional: Configurações globais para todas as instâncias
instances:
  - prometheus_plugin:
      url: http://<IP_DA_VM_RABBITMQ>:15692
      # Opcional: Para coletar métricas mais detalhadas (ex: por fila, exchange)
      # Descomente e ajuste o unaggregated_endpoint conforme a necessidade.
      # unaggregated_endpoint: detailed?family=queue_coarse_metrics&family=queue_consumer_count
    # Opcional: Tags personalizadas para esta instância
    tags:
      - env: production
      - service: rabbitmq-vm-externa
```

**Nota:** Substitua `<IP_DA_VM_RABBITMQ>` pelo IP real da sua VM. A URL aponta para a porta 15692, que é o endpoint do Prometheus.

### 2.3. Montar a Configuração no Cluster Agent

O arquivo `rabbitmq.yaml` deve ser montado no diretório de configuração do Cluster Agent (geralmente `/etc/datadog-agent/conf.d/rabbitmq.d/`).

#### Opção A: Usando o Datadog Operator (Recomendado)

Se você estiver usando o Datadog Operator, use o campo `extraConfd` para injetar a configuração diretamente no CRD `DatadogAgent`:

```yaml
apiVersion: datadoghq.com/v2alpha1
kind: DatadogAgent
metadata:
  name: datadog
spec:
  # ... (outras configurações)
  override:
    clusterAgent:
      extraConfd:
        configDataMap:
          rabbitmq.yaml: |-
            cluster_check: true
            init_config:
            instances:
              - prometheus_plugin:
                  url: http://<IP_DA_VM_RABBITMQ>:15692
                tags:
                  - env: production
                  - service: rabbitmq-vm-externa
```

#### Opção B: Usando Helm (Se não usar o Operator)

Se você estiver usando o Helm Chart do Datadog, adicione a configuração no seu arquivo `values.yaml` sob a seção `clusterAgent.confd`:

```yaml
# values.yaml
clusterAgent:
  confd:
    rabbitmq.yaml: |-
      cluster_check: true
      init_config:
      instances:
        - prometheus_plugin:
            url: http://<IP_DA_VM_RABBITMQ>:15692
          tags:
            - env: production
            - service: rabbitmq-vm-externa
```

Após aplicar a configuração, o Datadog Cluster Agent começará a executar a verificação do RabbitMQ e a enviar as métricas para o Datadog.

---

## Referências

[1] Datadog Docs. *Cluster Checks*. [https://docs.datadoghq.com/containers/cluster_agent/clusterchecks/](https://docs.datadoghq.com/containers/cluster_agent/clusterchecks/)
[2] Datadog Docs. *RabbitMQ Integration*. [https://docs.datadoghq.com/integrations/rabbitmq/](https://docs.datadoghq.com/integrations/rabbitmq/)
[3] RabbitMQ Documentation. *Monitoring with Prometheus and 
