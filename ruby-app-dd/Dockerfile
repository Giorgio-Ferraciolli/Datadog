FROM ruby:3.3-slim

RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cache de gems
COPY Gemfile ./
RUN bundle install --jobs 4

COPY . .

RUN chmod +x bin/start

EXPOSE 4567

CMD ["bin/start"]
