from django.urls import path
from . import views

urlpatterns = [
    path('startCalculation/', views.start_async_calculation, name='start-calculation'),
    path('taskStatus/<uuid:task_id>/', views.task_status, name='task-status'),
]