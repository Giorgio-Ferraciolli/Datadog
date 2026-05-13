# frozen_string_literal: true

require 'sequel'

DB = Sequel.connect(
  ENV.fetch('DATABASE_URL', 'postgres://postgres:postgres@db:5432/biblioteca'),
  max_connections: 10
)

# Permite alguns inflectors no Sequel
Sequel.extension :inflector
Sequel::Model.plugin :timestamps, update_on_create: true
