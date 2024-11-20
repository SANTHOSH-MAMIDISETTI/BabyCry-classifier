from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Home view
def home_view(request):
    # Redirecting to the login page for now
    return redirect('login')  # Or render a specific template if needed

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        from django.contrib.auth import authenticate, login
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'cry_classification/login.html', {'error': 'Invalid credentials'})
    return render(request, 'cry_classification/login.html')

# Dashboard view
@login_required
def dashboard_view(request):
    return render(request, 'cry_classification/dashboard.html')

def upload_audio_view(request):
    return render(request, 'cry_classification/upload_audio.html')
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, "Account created successfully. Please log in.")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
    
    return render(request, 'cry_classification/register.html')
