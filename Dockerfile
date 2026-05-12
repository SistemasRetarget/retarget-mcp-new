# Cloud Run Dockerfile para Rails 7 + PostgreSQL
# Multi-stage build: primero compilamos, luego corremos en imagen slim

FROM ruby:3.2-slim as builder

WORKDIR /app

# Instalar dependencias de build
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar Gemfile y Gemfile.lock
COPY Gemfile Gemfile.lock ./

# Instalar gemas
RUN bundle install --jobs 4 --retry 3

# Copiar código de la aplicación
COPY . .

# Stage 2: Imagen runtime slim
FROM ruby:3.2-slim

WORKDIR /app

# Instalar solo dependencias de runtime (no build-essential, compiladores, etc)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar gemas compiladas del builder
COPY --from=builder /usr/local/bundle /usr/local/bundle

# Copiar código de la aplicación
COPY --from=builder /app /app

# Asegurar que bundler está en el PATH
ENV PATH="/usr/local/bundle/bin:$PATH"

# Port que usa Cloud Run
EXPOSE 8080

# Health check (opcional pero recomendado)
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando para iniciar la aplicación
CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0", "-p", "8080"]
