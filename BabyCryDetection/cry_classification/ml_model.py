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

def predict_cry(features):
    # """
    # Predict the type of cry using the trained model.
    # :param audio_path: Path to the audio file
    # :return: Prediction label and confidence
    # """
    # # Extract features
    # y, sr = sf.read(audio_path)
    # if y.ndim > 1:  # Convert stereo to mono
    #     y = np.mean(y, axis=1)
    # mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    # features = np.mean(mfcc.T, axis=0).reshape(1, -1)

    # # Make predictions
    # prediction = model.predict(features)[0]
    # confidence = max(model.predict_proba(features)[0])

    # return prediction, confidence

    try:
        # Adjust features shape if necessary
        if features.ndim == 1 and features.shape[0] == 40:  # 1D array with 40 elements
            features_reshaped = features.reshape(1, -1)  # Reshape to (1, 40)
        elif features.ndim == 2 and features.shape == (1, 40):  # Already in the correct 2D shape
            features_reshaped = features
        else:
            raise ValueError(f"Invalid features shape: {features.shape}. Expected (40,) or (1, 40).")

        # Make predictions using the trained model
        prediction = model.predict(features_reshaped)[0]
        confidence = max(model.predict_proba(features_reshaped)[0])

        return prediction, confidence

    except Exception as e:
        raise ValueError(f"Error during prediction: {e}")
