FROM ruby:3.2-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar Gemfile (sin Gemfile.lock)
COPY Gemfile ./

# Instalar gemas
RUN bundle install --without development test

# Copiar código
COPY . .

# Port para Cloud Run
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando
CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0", "-p", "8080"]
