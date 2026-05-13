# frozen_string_literal: true

require_relative '../lib/db'
require_relative '../lib/models/book'
require_relative '../lib/models/reading_session'

if Book.count.positive?
  puts '🌱 Banco já populado, pulando seed.'
  exit
end

puts '🌱 Populando dados iniciais...'

books = [
  { title: 'Dom Casmurro',                 author: 'Machado de Assis',     genre: 'Romance',     total_pages: 256, status: 'finished' },
  { title: 'Grande Sertão: Veredas',       author: 'João Guimarães Rosa',  genre: 'Romance',     total_pages: 624, status: 'reading' },
  { title: 'Memórias Póstumas de Brás Cubas', author: 'Machado de Assis',  genre: 'Romance',     total_pages: 208, status: 'to_read' },
  { title: 'Vidas Secas',                  author: 'Graciliano Ramos',     genre: 'Romance',     total_pages: 175, status: 'finished' },
  { title: 'O Cortiço',                    author: 'Aluísio Azevedo',      genre: 'Romance',     total_pages: 304, status: 'to_read' },
  { title: 'Capitães da Areia',            author: 'Jorge Amado',          genre: 'Romance',     total_pages: 280, status: 'reading' }
]

books.each do |attrs|
  book = Book.create(attrs)

  if attrs[:status] == 'finished'
    pages_left = attrs[:total_pages]
    8.times do |i|
      pages = i == 7 ? pages_left : (pages_left / (8 - i)).clamp(20, 60)
      pages_left -= pages
      ReadingSession.create(
        book_id: book.id,
        pages: pages,
        read_on: Date.today - (8 - i) * 2,
        comment: i.zero? ? 'Começando o livro!' : nil
      )
    end
  elsif attrs[:status] == 'reading'
    3.times do |i|
      ReadingSession.create(
        book_id: book.id,
        pages: 40 + i * 10,
        read_on: Date.today - (3 - i),
        comment: nil
      )
    end
  end
end

puts "✅ #{Book.count} livros e #{ReadingSession.count} sessões criadas."
