# import os
# import cv2
# import dlib
# import numpy as np
# from flask import render_template, redirect, url_for, flash, request, Response, jsonify
# from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.utils import secure_filename
# from app import app, db
# from models import User
# from forms import LoginForm, UploadForm, SignupForm
# from utils import analyze_video, analyze_image
# from tensorflow.keras.models import load_model

# # Load the trained deepfake detection model
# model = load_model('attached_assets\deepfake-detection-model1.h5')  # Ensure this file exists

# # Initialize dlib's face detector
# detector = dlib.get_frontal_face_detector()

# ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov'}

# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Store latest analysis and video path
# latest_analysis = {'prediction': None, 'confidence': None}
# current_video_path = None

# def allowed_file(filename, file_type):
#     allowed_extensions = ALLOWED_IMAGE_EXTENSIONS if file_type == 'image' else ALLOWED_VIDEO_EXTENSIONS
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# @app.route('/')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))

#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user and user.check_password(form.password.data):
#             login_user(user)
#             return redirect(url_for('dashboard'))
#         flash('Invalid username or password', 'error')
#     return render_template('login.html', form=form)

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))

#     form = SignupForm()
#     if form.validate_on_submit():
#         if User.query.filter_by(username=form.username.data).first():
#             flash('Username already exists', 'error')
#             return render_template('signup.html', form=form)

#         if User.query.filter_by(email=form.email.data).first():
#             flash('Email already registered', 'error')
#             return render_template('signup.html', form=form)

#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Registration successful! Please login.', 'success')
#         return redirect(url_for('login'))

#     return render_template('signup.html', form=form)

# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('login'))

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     upload_form = UploadForm()
#     return render_template('dashboard.html', form=upload_form)

# @app.route('/upload/<file_type>', methods=['POST'])
# @login_required
# def upload_file(file_type):
#     global current_video_path
#     if 'file' not in request.files:
#         return {'error': 'No file part'}, 400

#     file = request.files['file']
#     if file.filename == '':
#         return {'error': 'No selected file'}, 400

#     if file and allowed_file(file.filename, file_type):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)

#         try:
#             if file_type == 'video':
#                 current_video_path = filepath  # Store for video streaming
#                 result = analyze_video(filepath)
#             else:  # image
#                 result = analyze_image(filepath)

#             if 'error' in result:
#                 return result, 400

#             # Store latest analysis
#             global latest_analysis
#             latest_analysis = result
#             return result

#         except Exception as e:
#             if os.path.exists(filepath):
#                 os.remove(filepath)
#             return {'error': str(e)}, 500

#     return {'error': 'Invalid file type'}, 400

# def generate_frames():
#     """Generate video frames with deepfake detection overlay."""
#     global current_video_path
#     if not current_video_path or not os.path.exists(current_video_path):
#         return

#     cap = cv2.VideoCapture(current_video_path)
#     if not cap.isOpened():
#         return

#     while cap.isOpened():
#         success, frame = cap.read()
#         if not success:
#             break

#         face_rects, _, _ = detector.run(frame, 0)

#         for d in face_rects:
#             x1, y1, x2, y2 = d.left(), d.top(), d.right(), d.bottom()
#             if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
#                 continue

#             crop_img = frame[y1:y2, x1:x2]
#             if crop_img.size == 0:
#                 continue

#             # Analyze frame
#             data = cv2.resize(crop_img, (128, 128)) / 255.0
#             data = np.expand_dims(data, axis=0)
#             prediction = model.predict(data)[0][0]
#             label = "Real Video" if prediction >= 0.5 else "Deepfake Video"

#             # Draw label and bounding box
#             cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
#             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

#         # Encode and send frame
#         _, buffer = cv2.imencode('.jpg', frame)
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

#     cap.release()
#     if os.path.exists(current_video_path):
#         os.remove(current_video_path)
#     current_video_path = None

# @app.route('/video_feed')
# @login_required
# def video_feed():
#     """Stream processed video frames"""
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/video_status')
# @login_required
# def video_status():
#     """Return latest analysis results"""
#     return jsonify(latest_analysis)
import os
import cv2
import dlib
import numpy as np
from flask import render_template, redirect, url_for, flash, request, Response, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db
from models import User
from forms import LoginForm, UploadForm, SignupForm
from utils import analyze_video, analyze_image
from tensorflow.keras.models import load_model

# Load the trained deepfake detection model
print("Step 1: Loading the deepfake detection model...")
model = load_model('attached_assets\deepfake-detection-model1.h5')  # Ensure this file exists
print("Model loaded successfully.")

# Initialize dlib's face detector
print("Step 2: Initializing dlib's face detector...")
detector = dlib.get_frontal_face_detector()
print("Face detector initialized.")

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov'}

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Store latest analysis and video path
latest_analysis = {'prediction': None, 'confidence': None}
current_video_path = None

def allowed_file(filename, file_type):
    allowed_extensions = ALLOWED_IMAGE_EXTENSIONS if file_type == 'image' else ALLOWED_VIDEO_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('signup.html', form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('signup.html', form=form)

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    upload_form = UploadForm()
    return render_template('dashboard.html', form=upload_form)

@app.route('/upload/<file_type>', methods=['POST'])
@login_required
def upload_file(file_type):
    global current_video_path
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400

    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    if file and allowed_file(file.filename, file_type):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Step 3: Saving uploaded file to {filepath}...")
        file.save(filepath)
        print("File saved successfully.")

        try:
            if file_type == 'video':
                current_video_path = filepath  # Store for video streaming
                print("Step 4: Analyzing video...")
                result = analyze_video(filepath)
            else:  # image
                print("Step 4: Analyzing image...")
                result = analyze_image(filepath)

            if 'error' in result:
                return result, 400

            # Store latest analysis
            global latest_analysis
            latest_analysis = result
            print("Analysis completed successfully.")
            return result

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            print(f"Error during analysis: {str(e)}")
            return {'error': str(e)}, 500

    return {'error': 'Invalid file type'}, 400

def generate_frames():
    global current_video_path
    if current_video_path is None:
        return None

    cap = cv2.VideoCapture(current_video_path)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        face_rects, scores, idx = detector.run(frame, 0)

        for i, d in enumerate(face_rects):
            x1, y1, x2, y2 = d.left(), d.top(), d.right(), d.bottom()
            if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
                continue

            cropped_face = frame[y1:y2, x1:x2]
            if cropped_face.size == 0:
                continue

            # Preprocess image
            resized_face = cv2.resize(cropped_face, (128, 128)) / 255.0
            processed_face = np.expand_dims(resized_face, axis=0)

            # Make prediction
            prediction = model.predict(processed_face)[0][0]
            predicted_class = 1 if prediction >= 0.5 else 0
            label = "Real Video" if predicted_class == 1 else "Deepfake Video"

            # Display result on the frame
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Stream frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/video_feed')
@login_required
def video_feed():
    """Stream processed video frames"""
    print("Step 13: Starting video feed...")
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_status')
@login_required
def video_status():
    """Return latest analysis results"""
    print("Step 14: Returning video status...")
    return jsonify(latest_analysis)