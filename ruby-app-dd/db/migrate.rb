# frozen_string_literal: true

require_relative '../lib/db'

puts '🗂  Criando schema...'

DB.create_table?(:books) do
  primary_key :id
  String  :title,       null: false
  String  :author,      null: false
  String  :genre
  Integer :total_pages
  String  :status,      null: false, default: 'to_read'
  Text    :notes
  DateTime :created_at
  DateTime :updated_at
end

DB.create_table?(:reading_sessions) do
  primary_key :id
  foreign_key :book_id, :books, null: false, on_delete: :cascade
  Integer :pages,  null: false
  Date    :read_on, null: false
  Text    :comment
  DateTime :created_at
  DateTime :updated_at

  index :book_id
  index :read_on
end

puts '✅ Schema pronto.'
