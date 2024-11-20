from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload_audio_view, name='upload_audio'),
    path('register/', views.register_view, name='register'),

]