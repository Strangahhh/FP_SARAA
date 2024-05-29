import uuid
from django.shortcuts import render, redirect
from ChatHub.models import ChatChannel
from .forms import RegisterForm, CustomAuthenticationForm
from django.contrib.auth import login, authenticate
from .models import CustomUser

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
