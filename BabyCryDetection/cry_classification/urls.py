# cry_classification/urls.py
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('history/', views.history_view, name='history'),
    path('upload/', views.upload_audio_view, name='upload_audio'),
    path('logout/', views.logout_view, name='logout'),
    path('help/', views.help_view, name='help'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)