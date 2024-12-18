# cry_classification/ml_model.py
import os
import pickle
import librosa
import soundfile as sf
import numpy as np

MODEL_PATH = os.path.join('model', 'model.pkl')

# Load the ML model
with open(MODEL_PATH, 'rb') as model_file:
    model = pickle.load(model_file)

def predict_cry(audio_path):
    """
    Predict the type of cry using the trained model.
    :param audio_path: Path to the audio file
    :return: Prediction label and confidence
    """
    # Extract features
    y, sr = sf.read(audio_path)
    if y.ndim > 1:  # Convert stereo to mono
        y = np.mean(y, axis=1)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    features = np.mean(mfcc.T, axis=0).reshape(1, -1)

    # Make predictions
    prediction = model.predict(features)[0]
    confidence = max(model.predict_proba(features)[0])

    return prediction, confidence
