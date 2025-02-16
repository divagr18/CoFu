from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.swot_analysis_view, name='swot_analysis'),
]