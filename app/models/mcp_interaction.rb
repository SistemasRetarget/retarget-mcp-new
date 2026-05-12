class McpInteraction < ApplicationRecord
  belongs_to :user

  store :data, accessors: [
    :ai_tool,
    :request_summary,
    :context_provided,
    :response_quality,
    :time_to_response,
    :user_action_after,
    :ip,
    :timestamp
  ]

  validates :user_id, presence: true
end
