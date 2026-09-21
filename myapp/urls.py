from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('channel/create/', create_channel_view, name='create_channel'),
    path('video/upload/', upload_video_view, name='upload_video'),
    path('watch/<int:video_id>/', watch_view, name='watch'),
    path('channel/<int:channel_id>/', channel_detail, name='channel_detail'),
    path('channel/<int:channel_id>/follow/', toggle_follow, name='toggle_follow'),
    path('video/<int:video_id>/like/', toggle_like, name='toggle_like'),
    path('profile/<str:username>/', user_profile, name='user_profile'),
]