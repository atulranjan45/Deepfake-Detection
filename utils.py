import cv2
import numpy as np
from tensorflow.keras.models import load_model
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize model variable
model = None

def load_deepfake_model():
    """Load the deepfake detection model"""
    global model
    if model is not None:
        return True
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'attached_assets', 'deepfake-detection-model1.h5')
        logger.info(f"Loading model from: {model_path}")
        if os.path.exists(model_path):
            model = load_model(model_path)
            logger.info("Model loaded successfully")
            return True
        else:
            logger.error(f"Model file not found at {model_path}")
            return False
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

def analyze_frame(frame):
    """Analyze a single frame for deepfake detection"""
    if not load_deepfake_model():
        return {'error': 'Model not loaded'}

    try:
        # Preprocess frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Ensure correct color format
        processed_frame = cv2.resize(frame, (128, 128))
        processed_frame = processed_frame / 255.0
        processed_frame = np.expand_dims(processed_frame, axis=0)

        # Make prediction
        prediction = model.predict(processed_frame, verbose=0)[0][0]
        confidence = float(abs(prediction - 0.5) * 2)  # Scale to 0-1

        return {
            'prediction': 'Real' if prediction >= 0.5 else 'Fake',
            'confidence': confidence
        }
    except Exception as e:
        logger.error(f"Error analyzing frame: {str(e)}")
        return {'error': str(e)}

def analyze_video(video_path):
    """Analyze video for deepfake detection"""
    if not load_deepfake_model():
        return {'error': 'Model not loaded'}

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error("Failed to open video file")
            return {'error': 'Failed to open video file'}

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        frame_interval = max(1, frame_rate)  # Extract at 1 frame per second
        predictions = []
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break  # End of video

            if frame_count % frame_interval == 0:
                result = analyze_frame(frame)
                if 'error' not in result:
                    predictions.append(1 if result['prediction'] == 'Real' else 0)
            
            frame_count += 1

        cap.release()

        if not predictions:
            return {'error': 'No frames could be analyzed'}

        # Average predictions
        final_prediction = np.mean(predictions)
        confidence = float(abs(final_prediction - 0.5) * 2)  # Scale to 0-1
        
        return {
            'prediction': 'Real' if final_prediction >= 0.5 else 'Fake',
            'confidence': confidence
        }
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        return {'error': str(e)}

def analyze_image(image_path):
    """Analyze image for deepfake detection"""
    if not load_deepfake_model():
        return {'error': 'Model not loaded'}

    try:
        # Read and process image
        img = cv2.imread(image_path)
        if img is None:
            return {'error': 'Failed to read image file'}

        return analyze_frame(img)
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return {'error': str(e)}