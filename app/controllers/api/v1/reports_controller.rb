module Api
  module V1
    class ReportsController < ApplicationController
      skip_before_action :verify_authenticity_token

      def adoption
        report = {
          total_users: User.count,
          active_users_week: User.joins(:mcp_interactions)
                                  .where('mcp_interactions.created_at > ?', 1.week.ago)
                                  .distinct.count,
          by_role: User.group(:role).count,
          by_ai_tool: User.group(:ai_tool).count,
          total_interactions: McpInteraction.count,
          interactions_last_week: McpInteraction.where('created_at > ?', 1.week.ago).count,
          average_response_quality: McpInteraction.average(:response_quality).to_f.round(2)
        }

        render json: report, status: :ok
      rescue => e
        Rails.logger.error("Error in reports#adoption: #{e.message}")
        render json: { error: 'Internal server error' }, status: :internal_server_error
      end

      def improvements
        report = {
          feedback_summary: {
            total: Feedback.count,
            by_type: Feedback.group(:feedback_type).count,
            average_rating: Feedback.where(feedback_type: :rating)
                                   .average('data->\'helpful\'').to_f.round(2)
          },
          top_suggestions: Feedback.where(feedback_type: :suggestion)
                                  .order(created_at: :desc)
                                  .limit(10)
                                  .pluck(:content),
          reported_issues: Feedback.where(feedback_type: :issue)
                                  .order(created_at: :desc)
                                  .limit(10)
                                  .pluck(:content)
        }

        render json: report, status: :ok
      rescue => e
        Rails.logger.error("Error in reports#improvements: #{e.message}")
        render json: { error: 'Internal server error' }, status: :internal_server_error
      end

      def roi
        total_interactions = McpInteraction.count
        avg_time_per_task = 2.5 # horas (estimado)
        cost_per_hour = 50 # USD (costo promedio equipo)

        time_saved = total_interactions * 0.5 # 30 min por interacción
        cost_savings = time_saved * cost_per_hour

        report = {
          total_interactions: total_interactions,
          estimated_time_saved_hours: time_saved.round(2),
          estimated_cost_savings: cost_savings.round(2),
          mcp_cost_monthly: 58.56,
          roi_percentage: ((cost_savings - 58.56) / 58.56 * 100).round(2),
          adoption_trend: adoption_trend_data
        }

        render json: report, status: :ok
      rescue => e
        Rails.logger.error("Error in reports#roi: #{e.message}")
        render json: { error: 'Internal server error' }, status: :internal_server_error
      end

      private

      def adoption_trend_data
        (0..6).map do |days_ago|
          date = days_ago.days.ago.to_date
          count = McpInteraction.where(created_at: date.beginning_of_day..date.end_of_day).count
          { date: date, interactions: count }
        end.reverse
      end
    end
  end
end
