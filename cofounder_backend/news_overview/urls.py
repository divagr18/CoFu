from django.urls import path
from . import views

urlpatterns = [
    path('overview/', views.news_overview_view, name='news_overview'),
]