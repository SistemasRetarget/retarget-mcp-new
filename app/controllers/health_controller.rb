class HealthController < ApplicationController
  skip_before_action :verify_authenticity_token

  def check
    render json: {
      status: 'ok',
      timestamp: Time.current,
      environment: Rails.env
    }, status: :ok
  end
end
