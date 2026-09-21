from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from django.db.models import Q


def index(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    videos = Video.objects.all()

    if query:
        videos = videos.filter(title__icontains=query)
    
    if category_id:
        videos = videos.filter(category_id=category_id)

    videos = videos.order_by('-created_at')
    categories = Category.objects.all()

    return render(request, 'index.html', {
        'videos': videos,
        'categories': categories,
    })


def register_view(request):
    error = None

    if request.method == 'POST':
        u_name = request.POST.get('username')
        u_pass = request.POST.get('password')
        u_pass_confirm = request.POST.get('password_confirm')

        if u_pass != u_pass_confirm:
            error = "Пароли не совпадают!"
        elif User.objects.filter(username=u_name).exists():
            error = "Пользователь с таким именем уже существует!"
        else:
            user = User.objects.create_user(username=u_name, password=u_pass)
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('index')

    return render(request, 'register.html', {'error': error})


def login_view(request):
    error = None
    if request.method == 'POST':
        u_name = request.POST.get('username')
        u_pass = request.POST.get('password')
        user = authenticate(username=u_name, password=u_pass)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            error = "Неверное имя пользователя или пароль!"

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='login')
def create_channel_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        avatar = request.FILES.get('avatar')

        if title and avatar:
            Channel.objects.create(
                title=title,
                description=description,
                avatar=avatar,
                owner=request.user
            )
            return redirect('user_profile', username=request.user.username)

    return render(request, 'create_channel.html')


@login_required(login_url='login')
def upload_video_view(request):
    user_channels = Channel.objects.filter(owner=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        thumbnail = request.FILES.get('thumbnail')
        video_file = request.FILES.get('video_file')
        category_id = request.POST.get('category')
        channel_id = request.POST.get('channel')

        category = None
        if category_id:
            category = Category.objects.filter(id=category_id).first()

        channel = None
        if channel_id:
            channel = Channel.objects.filter(id=channel_id, owner=request.user).first()

        if title and video_file and channel:
            Video.objects.create(
                title=title,
                description=description,
                thumbnail=thumbnail,
                video_file=video_file,
                category=category,
                channel=channel
            )
            return redirect('index')

    categories = Category.objects.all()
    return render(request, 'upload.html', {
        'categories': categories,
        'user_channels': user_channels
    })

def watch_view(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    video.views_count += 1
    video.save()

    recommended_videos = Video.objects.exclude(id=video_id).order_by('-created_at')[:8]
    comments = Comment.objects.filter(video=video).order_by('-created_at')
    likes_count = Like.objects.filter(video=video).count()

    is_following = False
    is_liked = False

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(user=request.user, channel=video.channel).exists()
        is_liked = Like.objects.filter(user=request.user, video=video).exists()

    subscribers_count = Follow.objects.filter(channel=video.channel).count()

    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('text')
        comment_id = request.POST.get('comment_id')

        if text:
            Comment.objects.create(
                user=request.user,
                video=video,
                text=text,
                comment_id=comment_id if comment_id else None
            )
            return redirect('watch', video_id=video_id)

    return render(request, 'watch.html', {
        'video': video,
        'recommended_videos': recommended_videos,
        'comments': comments,
        'likes_count': likes_count,
        'is_following': is_following,
        'is_liked': is_liked,
        'subscribers_count': subscribers_count,
    })


def channel_detail(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)
    videos = Video.objects.filter(channel=channel).order_by('-created_at')

    subscribers_count = Follow.objects.filter(channel=channel).count()
    total_likes = Like.objects.filter(video__channel=channel).count()

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(user=request.user, channel=channel).exists()

    return render(request, 'channel.html', {
        'channel': channel,
        'videos': videos,
        'subscribers_count': subscribers_count,
        'total_likes': total_likes,
        'is_following': is_following,
    })


@login_required(login_url='login')
def toggle_follow(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)

    if request.user != channel.owner:
        follow = Follow.objects.filter(user=request.user, channel=channel)
        if follow.exists():
            follow.delete()
        else:
            Follow.objects.create(user=request.user, channel=channel)

    return redirect('channel_detail', channel_id=channel_id)


@login_required(login_url='login')
def toggle_like(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    like = Like.objects.filter(user=request.user, video=video)

    if like.exists():
        like.delete()
    else:
        Like.objects.create(user=request.user, video=video)

    return redirect('watch', video_id=video_id)


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=profile_user)
    channels = Channel.objects.filter(owner=profile_user)

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'channels': channels,
    })