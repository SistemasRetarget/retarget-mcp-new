module Api
  module V1
    class ContextController < ApplicationController
      skip_before_action :verify_authenticity_token

      def show
        user = User.find(params[:user_id])
        context = ContextBuilder.new(user).build_context

        # Log interaction
        McpInteraction.create(
          user: user,
          data: {
            ai_tool: request.headers['X-AI-Tool'],
            request_summary: request.headers['X-Request-Summary'],
            timestamp: Time.current,
            ip: request.remote_ip
          }
        )

        render json: context, status: :ok
      rescue ActiveRecord::RecordNotFound
        render json: { error: 'User not found' }, status: :not_found
      rescue => e
        Rails.logger.error("Error in context#show: #{e.message}")
        render json: { error: 'Internal server error' }, status: :internal_server_error
      end

      def history
        user = User.find(params[:user_id])
        snapshots = user.context_snapshots
                        .order(created_at: :desc)
                        .limit(50)

        render json: snapshots.map(&:data), status: :ok
      rescue ActiveRecord::RecordNotFound
        render json: { error: 'User not found' }, status: :not_found
      end
    end
  end
end
