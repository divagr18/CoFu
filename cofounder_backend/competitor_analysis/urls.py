from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.competitor_analysis_view, name='competitor_analysis'),
]