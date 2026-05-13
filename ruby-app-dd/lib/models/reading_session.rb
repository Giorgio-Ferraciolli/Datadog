# frozen_string_literal: true

require_relative '../db'

class ReadingSession < Sequel::Model(:reading_sessions)
  many_to_one :book
end
