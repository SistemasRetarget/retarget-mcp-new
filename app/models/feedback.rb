class Feedback < ApplicationRecord
  belongs_to :user

  enum feedback_type: {
    suggestion: 0,
    rating: 1,
    issue: 2,
    usage_pattern: 3
  }

  store :data, accessors: [
    :ai_tool,
    :context_used,
    :helpful,
    :timestamp
  ]

  validates :user_id, :feedback_type, presence: true
end
