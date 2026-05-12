class ContextBuilder
  def initialize(user)
    @user = user
  end

  def build_context
    {
      user: user_data,
      active_tasks: fetch_tasks,
      recent_communications: fetch_communications,
      calendar: fetch_calendar,
      current_projects: fetch_projects,
      decisions_pending: fetch_decisions,
      metrics: fetch_metrics,
      timestamp: Time.current
    }
  end

  private

  def user_data
    {
      id: @user.id,
      name: @user.name,
      email: @user.email,
      role: @user.role,
      ai_tool: @user.ai_tool
    }
  end

  def fetch_tasks
    # Placeholder: Retorna tareas activas
    [
      {
        id: 1,
        title: "Tarea de ejemplo",
        status: "in_progress",
        created_at: Time.current
      }
    ]
  end

  def fetch_communications
    {
      emails: fetch_recent_emails,
      chat_messages: fetch_recent_chat
    }
  end

  def fetch_recent_emails
    # Placeholder: Emails recientes
    []
  end

  def fetch_recent_chat
    # Placeholder: Mensajes de chat recientes
    []
  end

  def fetch_calendar
    # Placeholder: Eventos próximos
    []
  end

  def fetch_projects
    # Placeholder: Proyectos activos
    []
  end

  def fetch_decisions
    # Placeholder: Decisiones pendientes
    []
  end

  def fetch_metrics
    {
      tasks_completed_week: 10,
      avg_time_per_task: 2.5,
      productivity_score: 0.92
    }
  end
end
