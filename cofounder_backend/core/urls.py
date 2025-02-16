from django.urls import path
from . import views

urlpatterns = [
    path('ask-gemini/', views.ask_gemini, name='ask_gemini'),
    path('get-csrf-token/', views.get_csrf_token_view, name='get_csrf_token'),
]