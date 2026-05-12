source "https://rubygems.org"
git_source(:github) { |repo| "https://github.com/#{repo}.git" }

ruby "3.2.0"

gem "rails", "~> 7.0.0"
gem "pg", "~> 1.1"
gem "puma", "~> 5.0"
gem "sass-rails", ">= 6"
gem "webpacker", "~> 5.0"
gem "turbolinks-rails"
gem "jbuilder", "~> 2.7"
gem "redis", "~> 4.0"
gem "bcrypt", "~> 3.1.7"
gem "image_processing", "~> 1.2"

# Google Cloud
gem "google-api-client", "~> 0.53.0"
gem "google-auth-library-ruby", "~> 1.4"
gem "google-cloud-secret-manager", "~> 1.0"
gem "google-cloud-tasks", "~> 2.0"
gem "google-cloud-logging", "~> 2.0"
gem "google-cloud-storage", "~> 1.40"

# API
gem "rack-cors"
gem "active_model_serializers", "~> 0.10.0"

# Background jobs
gem "sidekiq", "~> 6.0"

# Monitoring
gem "google-cloud-monitoring", "~> 1.0"

# Utilities
gem "dotenv-rails"
gem "httparty"

group :development, :test do
  gem "byebug", platforms: [:mri, :mingw, :x64_mingw]
  gem "rspec-rails", "~> 5.0"
  gem "factory_bot_rails", "~> 6.0"
  gem "faker"
end

group :development do
  gem "web-console", ">= 4.1.0"
  gem "listen", "~> 3.3"
  gem "spring"
end

group :production do
  gem "google-cloud-error-reporting", "~> 0.43.0"
end
