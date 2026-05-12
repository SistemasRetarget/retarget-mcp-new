# Dockerfile - Optimizado para Google Cloud Run
FROM ruby:3.2-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
  build-essential \
  postgresql-client \
  curl \
  git \
  && rm -rf /var/lib/apt/lists/*

# Copiar Gemfile
COPY Gemfile Gemfile.lock ./

# Instalar gemas (sin dev/test)
RUN bundle install --deployment --without development test

# Copiar código
COPY . .

# Precompilar assets
RUN bundle exec rake assets:precompile 2>/dev/null || true

# Crear directorio para logs
RUN mkdir -p log

# Exponer puerto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Comando de inicio
CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0", "-p", "8080"]
