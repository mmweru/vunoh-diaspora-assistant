from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/stats/', views.DashboardStatsView.as_view(), name='task-stats'),
    path('tasks/<str:task_code>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<str:task_code>/status/', views.TaskStatusUpdateView.as_view(), name='task-status-update'),
]
