from django.urls import path
from . import views

urlpatterns = [
    path('estimate/', views.market_size_view, name='market_size'),
]