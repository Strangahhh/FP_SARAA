import uuid
from django.shortcuts import get_object_or_404, render, redirect
from ChatHub.models import ChatChannel
from .forms import CustomUserForm, RegisterForm, CustomAuthenticationForm
from django.contrib.auth import login, authenticate
from .models import CustomUser
from django.contrib.auth.decorators import user_passes_test

def superuser_required(user):
    return user.is_superuser

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('login')
        else:
            return render(request, 'Authentication/register.html', {'form': form})
    else:
        form = RegisterForm()
    return render(request, 'Authentication/register.html', {'form': form})

def login_request(request):
    if request.method == 'POST':
        if 'email' in request.POST:
            email = request.POST.get('email')
            try:
                user = CustomUser.objects.get(email=email)
                request.session['user_email'] = user.email
                return render(request, 'Authentication/enter_password.html', {'email': email})
            except CustomUser.DoesNotExist:
                return render(request, 'Authentication/login.html', {'error': 'No user found with this email'})
        elif 'password' in request.POST:
            email = request.session.get('user_email')
            password = request.POST.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                existing_chat_channel = ChatChannel.objects.filter(user=user).first()
                if existing_chat_channel:
                    return redirect('chat_interface', chat_channel_uuid=existing_chat_channel.chat_uuid)
                else:
                    default_chat_channel = ChatChannel.objects.create(
                        user=user,
                        chat_name=f'Default Chat for {user.name}',
                        chat_uuid=uuid.uuid4()
                    )
                    return redirect('chat_interface', chat_channel_uuid=default_chat_channel.chat_uuid)
            else:
                return render(request, 'Authentication/enter_password.html', {'error': 'Invalid password', 'email': email})
    return render(request, 'Authentication/login.html')

@user_passes_test(superuser_required)
def management(request):
    chat_channels_back = ChatChannel.objects.filter(user=request.user)
    users = CustomUser.objects.all()
    user_data = []

    for user in users:
        chat_channels = ChatChannel.objects.filter(user=user)
        chat_count = chat_channels.count()
        user_data.append({
            'id': user.id,  # Ensure the ID is included
            'name': user.name,
            'email': user.email,
            'chat_count': chat_count,
            'is_staff': user.is_staff,
        })

    first_chat_channel_back = chat_channels_back.first() if chat_channels_back.exists() else None

    return render(request, 'Authentication/management.html', {
        'users': user_data,
        'first_chat_channel_back': first_chat_channel_back,
    })

@user_passes_test(superuser_required)
def create_user(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('management')
    else:
        form = CustomUserForm()
    return render(request, 'Authentication/user_form.html', {'form': form, 'title': 'Create User'})

@user_passes_test(superuser_required)
def update_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('management')
    else:
        form = CustomUserForm(instance=user)
    return render(request, 'Authentication/user_form.html', {'form': form, 'title': 'Update User'})

@user_passes_test(superuser_required)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('management')
    return render(request, 'Authentication/user_confirm_delete.html', {'user': user})