module Api
  module V1
    class FeedbackController < ApplicationController
      skip_before_action :verify_authenticity_token

      def create
        user = User.find(params[:user_id])

        feedback = Feedback.create(
          user: user,
          feedback_type: params[:type],
          content: params[:content],
          data: {
            ai_tool: params[:ai_tool],
            context_used: params[:context_used],
            helpful: params[:helpful],
            timestamp: Time.current
          }
        )

        if feedback.persisted?
          render json: { status: 'ok', feedback_id: feedback.id }, status: :created
        else
          render json: { errors: feedback.errors }, status: :unprocessable_entity
        end
      rescue ActiveRecord::RecordNotFound
        render json: { error: 'User not found' }, status: :not_found
      rescue => e
        Rails.logger.error("Error in feedback#create: #{e.message}")
        render json: { error: 'Internal server error' }, status: :internal_server_error
      end

      def index
        user = User.find(params[:user_id])
        feedbacks = user.feedbacks.order(created_at: :desc).limit(50)

        render json: feedbacks, status: :ok
      rescue ActiveRecord::RecordNotFound
        render json: { error: 'User not found' }, status: :not_found
      end
    end
  end
end
