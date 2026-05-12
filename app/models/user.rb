class User < ApplicationRecord
  has_many :context_snapshots, dependent: :destroy
  has_many :feedbacks, dependent: :destroy
  has_many :mcp_interactions, dependent: :destroy

  enum role: { jefe: 0, coo: 1, dev: 2, cm: 3, designer: 4, media: 5, seo: 6, journalist: 7 }
  enum ai_tool: { claude: 0, gemini: 1, chatgpt: 2 }

  validates :email, :role, :ai_tool, presence: true
  validates :email, uniqueness: true

  scope :ai_users, -> { where(is_ai_user: true) }
  scope :active, -> { where(active: true) }
end
