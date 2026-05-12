# Google Cloud Configuration
require "google/cloud/secret_manager"
require "google/cloud/logging"

# Load secrets from Secret Manager in production
if Rails.env.production?
  begin
    secret_manager = Google::Cloud::SecretManager.secret_manager_service
    project_id = ENV['GOOGLE_CLOUD_PROJECT']

    # Helper to fetch secrets
    def fetch_secret(secret_id)
      secret_manager = Google::Cloud::SecretManager.secret_manager_service
      project_id = ENV['GOOGLE_CLOUD_PROJECT']
      
      name = secret_manager.secret_version_path(
        project: project_id,
        secret: secret_id,
        secret_version: 'latest'
      )
      
      response = secret_manager.access_secret_version(request: { name: name })
      response.payload.data
    end

    # Load critical secrets
    ENV['DATABASE_URL'] ||= fetch_secret('DATABASE_URL')
    ENV['GOOGLE_CLIENT_ID'] ||= fetch_secret('GOOGLE_CLIENT_ID')
    ENV['GOOGLE_CLIENT_SECRET'] ||= fetch_secret('GOOGLE_CLIENT_SECRET')
    ENV['RAILS_MASTER_KEY'] ||= fetch_secret('RAILS_MASTER_KEY')
  rescue => e
    Rails.logger.warn("Could not load secrets from Secret Manager: #{e.message}")
  end

  # Setup Cloud Logging
  begin
    logging = Google::Cloud::Logging.new(
      project_id: ENV['GOOGLE_CLOUD_PROJECT']
    )
    
    Rails.logger = logging.logger "retarget-mcp"
    Rails.logger.level = Logger::INFO
  rescue => e
    Rails.logger.warn("Could not setup Cloud Logging: #{e.message}")
  end
end
