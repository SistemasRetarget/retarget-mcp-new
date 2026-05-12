class ContextSnapshot < ApplicationRecord
  belongs_to :user

  store :data, accessors: [
    :active_tasks,
    :recent_emails,
    :calendar_events,
    :chat_messages,
    :current_projects,
    :decisions_pending,
    :metrics
  ]

  validates :user_id, presence: true
end
