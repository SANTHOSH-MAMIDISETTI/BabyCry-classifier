import os
import librosa
import mimetypes
import numpy as np
import soundfile as sf
from django.conf import settings
from .ml_model import predict_cry
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils.timezone import now
from .models import PredictionHistory

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
    # Group uploads by day
    uploads_by_day = (
        PredictionHistory.objects
        .annotate(day=TruncDay('timestamp'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

    # Count cry predictions
    prediction_counts = (
        PredictionHistory.objects
        .values('prediction')
        .annotate(count=Count('id'))
    )

    # Prepare data for Chart.js
    uploads_labels = [entry['day'].strftime('%Y-%m-%d') for entry in uploads_by_day]
    uploads_data = [entry['total'] for entry in uploads_by_day]

    predictions_labels = [entry['prediction'] for entry in prediction_counts]
    predictions_data = [entry['count'] for entry in prediction_counts]

    context = {
        'total_uploads': PredictionHistory.objects.count(),
        'total_predictions': PredictionHistory.objects.filter(prediction="Crying Detected").count(),
        'uploads_labels': uploads_labels,
        'uploads_data': uploads_data,
        'predictions_labels': predictions_labels,
        'predictions_data': predictions_data,
    }
    return render(request, 'cry_classification/dashboard.html', context)

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

            # Extract features and predict
            features = extract_features(full_file_path)
            prediction, confidence = predict_cry(features)

            # print("---------- Just after predict -------")

            prediction_result = f"Prediction: {prediction} (Confidence: {confidence*100:.2f}%)"
            messages.success(request, f"File uploaded successfully! {prediction_result}")

            # Save prediction details to the database
            PredictionHistory.objects.create(
                user=request.user,
                file_name=audio_file.name,
                file_path=file_path,
                prediction=prediction,
                confidence=confidence * 100
            )

            # print("Just After something................")

        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
            return redirect('upload_audio')

        return redirect('dashboard')

    return render(request, 'cry_classification/upload_audio.html')

# Feature extraction function
def extract_features(file_path):
    try:
        # Load audio file
        audio, sample_rate = librosa.load(file_path, res_type="kaiser_fast")
        # Extract 40 MFCC features
        mfccs_features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        mfccs_scaled_features = np.mean(mfccs_features.T, axis=0)
        
        # Validate features length
        if len(mfccs_scaled_features) != 40:
            raise ValueError(f"Extracted features have {len(mfccs_scaled_features)} dimensions, but 40 were expected.")
        
        # Return as a 2D array for the classifier
        return mfccs_scaled_features.reshape(1, -1)
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

# History view
@login_required
def history_view(request):
    predictions = PredictionHistory.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'cry_classification/history.html', {'predictions': predictions})

# Help view
@login_required
def help_view(request):
    return render(request, 'cry_classification/help.html')
