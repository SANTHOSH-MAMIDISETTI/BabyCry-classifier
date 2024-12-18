# cry_classification/models.py
from django.db import models
from django.contrib.auth.models import User

class PredictionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user who made the prediction
    file_name = models.CharField(max_length=255)             # Name of the uploaded file
    file_path = models.CharField(max_length=500)             # Path to the file in the media directory
    prediction = models.CharField(max_length=255)            # Prediction result (e.g., "Crying Detected")
    confidence = models.FloatField()                         # Confidence score of the prediction
    timestamp = models.DateTimeField(auto_now_add=True)      # Timestamp of the prediction

    def __str__(self):
        return f"{self.user.username} - {self.file_name} - {self.prediction}"
