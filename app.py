from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from ultralytics import YOLO
import os
from dotenv import load_dotenv
import google.generativeai as genai
from werkzeug.utils import secure_filename
import base64
from PIL import Image
from io import BytesIO

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'static/results'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

# Load YOLOv8 model
model = YOLO('model.pt')

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/deteksi', methods=['POST'])
def deteksi():
    if 'image' not in request.files:
        return redirect(url_for('home'))
    
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('home'))
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Deteksi menggunakan YOLOv8
    results = model(filepath)
    
    if results and results[0].boxes:
        labels = [model.model.names[int(cls)] for cls in results[0].boxes.cls]
        confs = [float(conf) for conf in results[0].boxes.conf]
        boxes = results[0].boxes.xyxy.cpu().numpy().tolist()
        
        # Simpan gambar hasil deteksi ke folder static/results
        result_img_path = os.path.join(app.config['RESULT_FOLDER'], filename)
        results[0].save(result_img_path)
        
        # Untuk ditampilkan di template (relative path)
        result_img = f'results/{filename}'
        
        # Gabungkan info deteksi
        detections = [
            {'label': label, 'confidence': conf, 'box': box}
            for label, conf, box in zip(labels, confs, boxes)
        ]
        result = ', '.join(labels)
    else:
        result = 'Tidak terdeteksi penyakit pada gambar.'
        result_img = None
        detections = []
    
    # Store detection results in session for the detection page
    session['detection_results'] = {
        'result': result,
        'result_img': result_img,
        'detections': detections,
        'original_filename': filename
    }
    
    return redirect(url_for('detection'))

@app.route('/detection')
def detection():
    # Get detection results from session
    detection_results = session.get('detection_results', None)
    
    if not detection_results:
        return redirect(url_for('home'))
    
    return render_template(
        'detection.html',
        result=detection_results['result'],
        result_img=detection_results['result_img'],
        detections=detection_results['detections'],
        original_filename=detection_results['original_filename']
    )

@app.route('/realtime', methods=['GET'])
def realtime():
    return render_template('realtime.html')

@app.route('/realtime_detect', methods=['POST'])
def realtime_detect():
    data = request.json['image']
    header, encoded = data.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    img = Image.open(BytesIO(img_bytes))
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'webcam.jpg')
    img.save(img_path)

    results = model(img_path)
    if results and results[0].boxes:
        labels = [model.model.names[int(cls)] for cls in results[0].boxes.cls]
        confs = [float(conf) for conf in results[0].boxes.conf]
        boxes = results[0].boxes.xyxy.cpu().numpy().tolist()
        detections = [
            {'label': label, 'confidence': conf, 'box': box}
            for label, conf, box in zip(labels, confs, boxes)
        ]
        result = ', '.join(labels)
    else:
        detections = []
        result = 'Tidak terdeteksi penyakit pada gambar.'

    return jsonify({'result': result, 'detections': detections})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    
    if not data or 'message' not in data or 'disease' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    user_message = data['message']
    disease = data['disease']
    
    # Create a context-aware prompt for Gemini that specifies Indonesian response with Markdown
    prompt = f"""
    You are a plant disease expert specializing in strawberry diseases. Provide helpful information about the following:
    
    Disease detected: {disease}
    
    User question: {user_message}
    
    Respond in Indonesian language only. Format your response using Markdown (with ** for bold, * for bullet points, etc.).
    
    Provide a concise, helpful response focusing on:
    - Brief description of the disease
    - Typical symptoms
    - Potential treatments or management practices
    - Prevention methods
    
    Keep your response professional but easy to understand for farmers and gardeners.
    """
    
    try:
        # Generate response from Gemini
        response = gemini_model.generate_content(prompt)
        
        return jsonify({
            'response': response.text,
            'disease': disease
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)