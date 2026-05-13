# frozen_string_literal: true

require_relative '../db'

class Book < Sequel::Model(:books)
  one_to_many :reading_sessions

  STATUSES = %w[to_read reading finished].freeze
  STATUS_LABELS = {
    'to_read'  => 'A ler',
    'reading'  => 'Lendo',
    'finished' => 'Finalizado'
  }.freeze

  def status_label
    STATUS_LABELS.fetch(status, status)
  end

  def pages_read
    reading_sessions_dataset.sum(:pages) || 0
  end

  def progress_pct
    return 0 if total_pages.nil? || total_pages.zero?

    pct = (pages_read.to_f / total_pages * 100).round
    [pct, 100].min
  end
end
