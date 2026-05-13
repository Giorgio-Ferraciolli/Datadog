# frozen_string_literal: true

# Carrega libs primeiro
require 'sinatra'
require 'sinatra/contrib'
require_relative 'lib/db'
require_relative 'lib/models/book'
require_relative 'lib/models/reading_session'

# Datadog tracer DEPOIS das libs (precisa detectá-las já carregadas)
require_relative 'lib/tracing'

set :bind, '0.0.0.0'
set :port, 4567
set :views, File.expand_path('views', __dir__)
set :public_folder, File.expand_path('public', __dir__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
helpers do
  def h(text)
    Rack::Utils.escape_html(text.to_s)
  end

  def fmt_date(d)
    return '' if d.nil?

    d.strftime('%d/%m/%Y')
  end
end

# Shortcut para criar spans manuais
def trace(name, &block)
  Datadog::Tracing.trace(name, &block)
end

# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

# Home — lista de livros, com filtro opcional por status
get '/' do
  trace('home.list_books') do |span|
    status_filter = params['status']
    span.set_tag('filter.status', status_filter || 'all')

    books = trace('db.fetch_books') do |inner|
      ds = Book.order(Sequel.desc(:updated_at))
      ds = ds.where(status: status_filter) if Book::STATUSES.include?(status_filter)
      result = ds.all
      inner.set_tag('db.rows_returned', result.size)
      result
    end

    counters = trace('db.compute_counters') do
      {
        all:      Book.count,
        to_read:  Book.where(status: 'to_read').count,
        reading:  Book.where(status: 'reading').count,
        finished: Book.where(status: 'finished').count
      }
    end

    span.set_tag('books.shown', books.size)
    erb :index, locals: { books: books, counters: counters, active: status_filter }
  end
end

# Página de novo livro
get '/books/new' do
  erb :new_book, locals: { errors: [], book: {} }
end

# Criar livro
post '/books' do
  trace('book.create') do |span|
    attrs = {
      title:       params['title'].to_s.strip,
      author:      params['author'].to_s.strip,
      genre:       params['genre'].to_s.strip,
      total_pages: params['total_pages'].to_s.empty? ? nil : params['total_pages'].to_i,
      status:      params['status'].to_s.strip,
      notes:       params['notes'].to_s.strip
    }

    errors = []
    errors << 'Título é obrigatório'      if attrs[:title].empty?
    errors << 'Autor é obrigatório'       if attrs[:author].empty?
    errors << 'Status inválido'           unless Book::STATUSES.include?(attrs[:status])

    if errors.any?
      span.set_tag('validation.failed', true)
      span.set_tag('validation.errors', errors.join('; '))
      halt erb(:new_book, locals: { errors: errors, book: attrs })
    end

    book = Book.create(attrs)
    span.set_tag('book.id', book.id)
    span.set_tag('book.title', book.title)

    redirect "/books/#{book.id}"
  end
end

# Detalhe do livro
get '/books/:id' do
  trace('book.show') do |span|
    span.set_tag('book.id', params['id'])

    book = trace('db.find_book') { Book[params['id'].to_i] }
    halt 404, 'Livro não encontrado' unless book

    sessions = trace('db.fetch_sessions') do |inner|
      result = book.reading_sessions_dataset.order(Sequel.desc(:read_on)).all
      inner.set_tag('sessions.count', result.size)
      result
    end

    pages_read = trace('book.compute_progress') do |inner|
      total = sessions.sum(&:pages)
      inner.set_tag('book.pages_read', total)
      inner.set_tag('book.total_pages', book.total_pages || 0)
      total
    end

    erb :book, locals: { book: book, sessions: sessions, pages_read: pages_read }
  end
end

# Registrar sessão de leitura
post '/books/:id/sessions' do
  trace('reading_session.create') do |span|
    span.set_tag('book.id', params['id'])

    book = Book[params['id'].to_i]
    halt 404, 'Livro não encontrado' unless book

    pages = params['pages'].to_i
    if pages <= 0
      span.set_tag('validation.failed', true)
      halt 400, 'Número de páginas inválido'
    end

    session = trace('db.insert_session') do
      ReadingSession.create(
        book_id: book.id,
        pages:   pages,
        read_on: params['read_on'].to_s.empty? ? Date.today : Date.parse(params['read_on']),
        comment: params['comment'].to_s.strip
      )
    end

    span.set_tag('session.id', session.id)
    span.set_tag('session.pages', pages)

    # Auto-marca como "finished" se atingiu o total
    if book.total_pages && book.pages_read >= book.total_pages && book.status != 'finished'
      trace('book.auto_finish') do
        book.update(status: 'finished')
      end
    elsif book.status == 'to_read'
      trace('book.auto_start') do
        book.update(status: 'reading')
      end
    end

    redirect "/books/#{book.id}"
  end
end

# Deletar livro
post '/books/:id/delete' do
  trace('book.delete') do |span|
    span.set_tag('book.id', params['id'])
    book = Book[params['id'].to_i]
    halt 404 unless book
    book.destroy
  end
  redirect '/'
end

# Página de estatísticas — muitos spans em uma requisição
get '/stats' do
  trace('stats.compute') do |span|
    totals = trace('stats.totals') do
      {
        books:    Book.count,
        finished: Book.where(status: 'finished').count,
        reading:  Book.where(status: 'reading').count,
        to_read:  Book.where(status: 'to_read').count,
        sessions: ReadingSession.count,
        pages:    ReadingSession.sum(:pages) || 0
      }
    end

    by_genre = trace('stats.by_genre') do |inner|
      result = Book
               .where(Sequel.~(genre: nil))
               .group_and_count(:genre)
               .order(Sequel.desc(:count))
               .all
               .map { |r| [r[:genre], r[:count]] }
      inner.set_tag('stats.genres_count', result.size)
      result
    end

    last_7_days = trace('stats.last_7_days') do
      since = Date.today - 6
      ReadingSession
        .where { read_on >= since }
        .group(:read_on)
        .select_map([:read_on, Sequel.function(:sum, :pages).as(:total)])
        .map { |d, t| [d, t.to_i] }
        .to_h
    end

    span.set_tag('stats.total_books', totals[:books])
    span.set_tag('stats.total_pages_read', totals[:pages])

    erb :stats, locals: { totals: totals, by_genre: by_genre, last_7_days: last_7_days }
  end
end

# Healthcheck
get '/health' do
  content_type :json
  { status: 'ok', db: DB.test_connection ? 'up' : 'down' }.to_json
end
