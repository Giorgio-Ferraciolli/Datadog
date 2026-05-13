# frozen_string_literal: true

# IMPORTANTE: deve ser carregado DEPOIS de sinatra/pg/sequel já estarem
# requeridos, para que o Datadog detecte e instrumente as libs corretamente.

require 'datadog'

Datadog.configure do |c|
  # Identificação do serviço — também vem de DD_SERVICE/DD_ENV/DD_VERSION
  # (env vars têm prioridade)
  c.service = 'biblioteca-pessoal'
  c.env     = ENV.fetch('DD_ENV', 'development')
  c.version = '1.0.0'
  c.remote.enabled = false

  # Auto-instrumentações
  c.tracing.instrument :sinatra
  c.tracing.instrument :pg, service_name: 'biblioteca-pg'

  # Tags globais aplicadas a todos os spans
  c.tags = {
    'team'  => 'observability-study',
    'stack' => 'ruby-sinatra'
  }
end
