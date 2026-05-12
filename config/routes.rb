Rails.application.routes.draw do
  # Health check for Cloud Run
  get '/health', to: 'health#check'

  namespace :api do
    namespace :v1 do
      # Context endpoints
      get '/context/:user_id', to: 'context#show'
      get '/context/:user_id/history', to: 'context#history'

      # Feedback endpoints
      post '/feedback', to: 'feedback#create'
      get '/feedback/:user_id', to: 'feedback#index'

      # Reports endpoints
      get '/reports/adoption', to: 'reports#adoption'
      get '/reports/improvements', to: 'reports#improvements'
      get '/reports/roi', to: 'reports#roi'

      # Webhooks
      post '/webhooks/gmail', to: 'webhooks#gmail'
      post '/webhooks/chat', to: 'webhooks#chat'
      post '/webhooks/calendar', to: 'webhooks#calendar'
    end
  end

  # Admin routes (opcional)
  namespace :admin do
    root 'dashboard#index'
    resources :users
    resources :feedback
  end
end
