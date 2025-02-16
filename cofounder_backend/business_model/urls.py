from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.business_model_view, name='business_model'),
]