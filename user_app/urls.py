from django.urls import path
from . import views
from .views import CustomUserAPIView
urlpatterns = [
    path('api/signup/', CustomUserAPIView.as_view(), name='user_signup'),
    path('signup/', views.signup, name='signup'),
    path('test/', views.test, name='test'),
    path('fail/', views.fail, name='fail'),
    path('stream/', views.stream_camera, name='stream_camera'),
]