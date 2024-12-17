import os
import librosa
import mimetypes
import numpy as np
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

# Mock Model Prediction (Placeholder)
def mock_model_predict(features):
    return 1 if np.mean(features) > 0.5 else 0

# Home view
def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password. Please try again.")
        else:
            messages.error(request, "Both username and password are required.")

    return render(request, 'cry_classification/login.html')

# Register view
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not all([username, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return render(request, 'cry_classification/register.html', {
                'username': username,
                'email': email
            })

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'cry_classification/register.html', {
                'username': username,
                'email': email
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another one.")
            return render(request, 'cry_classification/register.html', {
                'username': username,
                'email': email
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'cry_classification/register.html', {
                'username': username,
                'email': email
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'cry_classification/register.html', {
                'username': username,
                'email': email
            })

    return render(request, 'cry_classification/register.html')

# Dashboard view
@login_required
def dashboard_view(request):
    return render(request, 'cry_classification/dashboard.html')

# Upload audio view
@login_required
def upload_audio_view(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']

        # File size validation
        max_file_size_mb = 10
        if audio_file.size > max_file_size_mb * 1024 * 1024:
            messages.error(request, f"File size exceeds {max_file_size_mb} MB. Please upload a smaller file.")
            return redirect('upload_audio')

        # Validate the file type using MIME type
        mime_type, _ = mimetypes.guess_type(audio_file.name)
        if not mime_type or not mime_type.startswith('audio'):
            messages.error(request, "Invalid file type. Please upload an audio file.")
            return redirect('upload_audio')

        # Validate the file extension
        valid_extensions = ['.mp3', '.wav', '.ogg', '.flac', '.m4a']
        file_extension = os.path.splitext(audio_file.name)[1].lower()
        if file_extension not in valid_extensions:
            messages.error(request, f"Invalid file extension. Supported extensions are: {', '.join(valid_extensions)}")
            return redirect('upload_audio')

        # Save the file to the media directory
        try:
            file_path = default_storage.save(f'audio_files/{audio_file.name}', ContentFile(audio_file.read()))
            full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # Validate and process the saved file
            y, sr = librosa.load(full_file_path, sr=None)

            # Extract features and predict
            features = extract_features(full_file_path)
            prediction = mock_model_predict(features)

            prediction_result = "Crying Detected" if prediction == 1 else "No Crying Detected"
            messages.success(request, f"File uploaded successfully! Prediction: {prediction_result}")

        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
            return redirect('upload_audio')

        return redirect('dashboard')

    return render(request, 'cry_classification/upload_audio.html')

# Feature extraction function
def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        return np.mean(mfcc.T, axis=0)
    except Exception as e:
        raise ValueError(f"Error extracting features: {e}")

# Logout view
@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('login')

    return render(request, 'cry_classification/logout_confirmation.html')


@login_required
def history_view(request):
    predictions = [
        {"date": "2024-12-18 10:30", "file_name": "cry1.wav", "result": "Crying Detected", "confidence": 85.5},
        {"date": "2024-12-18 11:00", "file_name": "cry2.wav", "result": "No Crying Detected", "confidence": 76.3},
    ]
    return render(request, 'cry_classification/history.html', {'predictions': predictions})

@login_required
def help_view(request):
    return render(request, 'cry_classification/help.html')
