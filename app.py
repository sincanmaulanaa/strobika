from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from ultralytics import YOLO
import os
from dotenv import load_dotenv
import google.generativeai as genai
from werkzeug.utils import secure_filename
import base64
from PIL import Image
from io import BytesIO
import time
import numpy as np
from werkzeug.middleware.proxy_fix import ProxyFix


print("🔥 Mulai eksekusi app.py")

load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['RESULT_FOLDER'] = os.path.join('static', 'results')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

print("📦 Cek model path:", os.path.exists("best.pt"))

try:
    print("🔍 Inisialisasi YOLO model...")
    model = YOLO('best.pt')
    print("✅ Model loaded")
except Exception as e:
    print("❌ Gagal load model:", e)
    model = None


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
        time.sleep(1)
        
        # Untuk ditampilkan di template (URL absolut)
        result_img = url_for('static', filename=f'results/{filename}', _external=True)

        
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

    # Wait until image is fully saved
    for _ in range(10):  # up to ~2s
        if os.path.exists(result_img_path):
            break
        time.sleep(0.2)

    
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
        original_filename=detection_results['original_filename'],
        current_time=int(time.time())  # tambahan untuk cache-busting
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

    # Save original webcam image
    filename = f'webcam_{int(time.time())}.jpg'
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img.save(img_path)

    # Run detection on the image
    results = model(img_path)

    result_img_path = os.path.join(app.config['RESULT_FOLDER'], filename)

    if results and results[0].boxes:
        labels = [model.model.names[int(cls)] for cls in results[0].boxes.cls]
        confs = [float(conf) for conf in results[0].boxes.conf]
        boxes = results[0].boxes.xyxy.cpu().numpy().tolist()

        # Save annotated image
        results[0].save(result_img_path)

        result = ', '.join(labels)
        detections = [
            {'label': label, 'confidence': conf, 'box': box}
            for label, conf, box in zip(labels, confs, boxes)
        ]
    else:
        # Save original image as fallback
        img.save(result_img_path)
        result = 'Tidak terdeteksi penyakit pada gambar.'
        detections = []

    # ✅ Pastikan file benar-benar tersedia sebelum digunakan
    for _ in range(10):
        if os.path.exists(result_img_path):
            break
        time.sleep(0.2)

    result_img = url_for('static', filename=f'results/{filename}', _external=True)

    session['detection_results'] = {
        'result': result,
        'result_img': result_img,
        'detections': detections,
        'original_filename': 'Gambar dari Webcam',
        'source': 'realtime'
    }

    return jsonify({'redirect': url_for('detection')})


@app.route('/realtime_detect_continuous', methods=['POST'])
def realtime_detect_continuous():
    data = request.json['image']
    header, encoded = data.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    img = Image.open(BytesIO(img_bytes))
    
    # Process image without saving to disk for faster response
    # Convert PIL Image to numpy array for detection
    img_array = np.array(img)
    
    # Run detection on the image
    results = model(img_array)
    
    detection_results = []
    
    if results and results[0].boxes:
        boxes = results[0].boxes.xyxy.cpu().numpy().tolist()
        labels = [model.model.names[int(cls)] for cls in results[0].boxes.cls]
        confs = [float(conf) for conf in results[0].boxes.conf]
        
        # Format results for JSON response
        for label, conf, box in zip(labels, confs, boxes):
            detection_results.append({
                'label': label,
                'confidence': conf,
                'box': box
            })
    
    return jsonify({
        'detections': detection_results
    })

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    
    if not data or 'message' not in data or 'disease' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    user_message = data['message']
    disease = data['disease']
    
    # Updated prompt with better greeting handling
    prompt = f"""
    You are a plant disease expert specializing in strawberry diseases, your name is Strobot. 
    
    Disease detected: {disease}
    User question: {user_message}
    
    IMPORTANT CLASSIFICATION INSTRUCTIONS:
    
    OFF-TOPIC: If the question is clearly unrelated to these topics (like asking about politics, entertainment, other crops, or personal questions), respond ONLY with: "Mohon maaf, saya hanya dapat menjawab pertanyaan seputar penyakit tanaman stroberi dan perawatannya."
    
    Examples of OFF-TOPIC questions you should NOT answer:
    - "Siapa presiden Indonesia?"
    - "Berapa harga Bitcoin hari ini?"
    - "Bagaimana cara memasak nasi goreng?"
    - "Ceritakan tentang kehidupan pribadi kamu"
    - "Apakah kamu bisa membantu saya mengerjakan PR matematika?"
    
    Always be direct and avoid lengthy explanations unless specifically asked for details.
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