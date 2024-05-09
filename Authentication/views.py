from django.shortcuts import render, redirect
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
                return redirect('ChatInterface')
            else:
                return render(request, 'Authentication/enter_password.html', {'error': 'Invalid password', 'email': email})

    return render(request, 'Authentication/login.html')
