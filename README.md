# Strobika - Strawberry Leaf Disease Detection System

![Strobika Logo](static/images/logo.png)

## 📝 Project Description

Strobika is an AI-powered web application designed to detect diseases in strawberry plant leaves. The application uses a YOLOv8 model to quickly and accurately identify various types of strawberry leaf diseases, helping farmers and hobbyists diagnose problems with their strawberry plants.

## ✨ Key Features

- **Disease Detection**: Upload strawberry leaf images for instant disease identification
- **Realtime Detection**: Use your webcam for live disease detection
- **AI Assistant**: Integrated chatbot using Gemini API to provide information and solutions for detected diseases
- **Detailed Results**: Visualization of detection results with accuracy levels and disease locations
- **Responsive Interface**: Modern design that works well across various devices

## 🛠️ Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI/ML**: YOLOv8 for object detection
- **LLM**: Google Gemini API for chatbot
- **Media Processing**: OpenCV, PIL

## 📋 Prerequisites

- Python 3.8 or newer
- pip (Python package manager)
- Webcam (for realtime detection feature)

## 🚀 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/sincanmaulanaa/strobika.git
   cd strobika
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   # or
   venv\Scripts\activate  # For Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download YOLOv8 model**

   ```bash
   # Ensure model.pt is in the main application directory
   # If not available, download from the appropriate source
   ```

5. **Configure Gemini API Key**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a .env file in the root directory with `GEMINI_API_KEY=your_api_key_here`

## 🔧 Usage

1. **Run the application**

   ```bash
   python app.py
   ```

2. **Access the application**

   - Open a web browser and navigate to `http://localhost:5000`

3. **Disease Detection**

   - Select a strawberry leaf image from your device or
   - Drag and drop an image to the upload area
   - Click the "Detect" button

4. **Realtime Detection**

   - Click the "Realtime Detection with Webcam" button
   - Allow camera access if prompted
   - Point your camera at strawberry leaves and click "Detect Now"

5. **Consult with the Chatbot**
   - On the results page, click the chatbot icon in the bottom right corner
   - Ask questions about the detected disease

## 📂 Project Structure

```
strobika/
├── app.py                 # Main Flask application file
├── model.pt               # Trained YOLOv8 model
├── requirements.txt       # Python dependencies
├── static/                # Static assets
│   ├── css/               # Stylesheet files
│   │   └── style.css      # Main stylesheet
│   ├── images/            # Images and icons
│   │   └── logo.png       # Strobika logo
│   └── results/           # Stored detection results
├── templates/             # HTML templates
│   ├── index.html         # Main page
│   ├── detection.html     # Detection results page
│   └── realtime.html      # Realtime detection page
└── uploads/               # Uploaded image storage
```

## 🔄 API Endpoints

| Endpoint           | Method | Description                                     |
| ------------------ | ------ | ----------------------------------------------- |
| `/`                | GET    | Main application page                           |
| `/deteksi`         | POST   | Receives uploaded image and processes detection |
| `/detection`       | GET    | Displays detection results                      |
| `/realtime`        | GET    | Realtime detection page with webcam             |
| `/realtime_detect` | POST   | Processes images from webcam                    |
| `/chatbot`         | POST   | Endpoint for chatbot interaction                |

## 📦 Main Dependencies

- Flask
- Ultralytics YOLOv8
- Google Generative AI
- OpenCV
- Pillow
- Werkzeug

See requirements.txt for a complete list of dependencies and their versions.

## 📊 Detectable Disease Classes

- Leaf Spot
- Powdery Mildew
- Leaf Rust
- Gray Mold
- Healthy Leaf

## 📝 Usage Notes

- For best detection results, use images with good lighting
- Images should be clear and focused on strawberry leaves
- Image upload size limit: 5MB
- Supported image formats: JPG, PNG, GIF

## 👥 Contribution

Contributions to improve Strobika are highly appreciated! If you'd like to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Contact

Project Name: Strobika - Strawberry Leaf Disease Detection System  
Email: sincanmaulanaa@gmail.com

---

Made with ❤️ for strawberry farmers and the agricultural community
