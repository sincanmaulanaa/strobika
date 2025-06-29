import os
import json
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image
import numpy as np
import base64
from app import app as flask_app

@pytest.fixture
def app():
    """Flask application fixture."""
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key",
        "UPLOAD_FOLDER": "/tmp/test_uploads",
        "RESULT_FOLDER": "static/test_results"
    })
    
    # Create test directories
    os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(flask_app.config['RESULT_FOLDER'], exist_ok=True)
    
    yield flask_app
    
    # Cleanup after tests
    for folder in [flask_app.config['UPLOAD_FOLDER'], flask_app.config['RESULT_FOLDER']]:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)

@pytest.fixture
def client(app):
    """Test client for the Flask application."""
    return app.test_client()

@pytest.fixture
def mock_yolo_results():
    """Mock YOLO detection results."""
    class MockResultsList(list):
        def __bool__(self):
            return True
        def __getitem__(self, index):
            if index == 0:
                return self.first_result
            raise IndexError("Index out of range")
    
    # Create the results list
    results = MockResultsList()
    
    # Create a single result with boxes
    result = MagicMock()
    boxes = MagicMock()
    
    # Configure boxes
    boxes.__bool__.return_value = True
    # Set up classes and confidences as Python lists instead of numpy arrays
    boxes.cls = [0, 1]
    boxes.conf = [0.95, 0.87]
    
    # Set up the xyxy chain
    mock_numpy = MagicMock()
    mock_numpy.tolist.return_value = [[10, 20, 100, 200], [30, 40, 120, 220]]
    
    mock_cpu = MagicMock()
    mock_cpu.numpy.return_value = mock_numpy
    
    mock_xyxy = MagicMock()
    mock_xyxy.cpu.return_value = mock_cpu
    
    boxes.xyxy = mock_xyxy
    
    # Set up the result
    result.boxes = boxes
    results.first_result = result
    
    # Mock the model names
    mock_model = MagicMock()
    mock_model.names = {0: 'Leaf Scorch', 1: 'Powdery Mildew'}
    results.model = mock_model
    
    return results

@pytest.fixture
def test_image():
    """Create a test image."""
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io

@patch('app.model')
def test_deteksi_route_no_file(mock_model, client):
    """Test /deteksi redirects to home when no file provided."""
    response = client.post('/deteksi', follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith('/')

@patch('app.model')
def test_deteksi_route_empty_filename(mock_model, client):
    """Test /deteksi redirects to home when empty filename provided."""
    response = client.post('/deteksi', data={'image': (BytesIO(), '')}, follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith('/')

@patch('app.model')
def test_deteksi_route_with_file(mock_model, client, test_image, mock_yolo_results):
    """Test /deteksi route with a valid file upload."""
    # Mock model to return our mocked results
    mock_model.return_value = mock_yolo_results
    
    # Create a test file upload
    response = client.post(
        '/deteksi',
        data={'image': (test_image, 'test_image.jpg')},
        follow_redirects=False
    )
    
    # Should redirect to detection page
    assert response.status_code == 302
    assert response.location.endswith('/detection')
    
    # Check that model was called
    mock_model.assert_called_once()

@patch('app.model')
@patch('app.gemini_model.generate_content')
def test_chatbot_route(mock_generate_content, mock_model, client):
    """Test the chatbot API endpoint."""
    # Mock Gemini API response
    mock_response = MagicMock()
    mock_response.text = "This is a response about strawberry diseases."
    mock_generate_content.return_value = mock_response
    
    # Test data
    test_data = {
        'message': 'How do I treat leafspot?',
        'disease': 'Leafspot'
    }
    
    # Send request
    response = client.post(
        '/chatbot',
        json=test_data,
        content_type='application/json'
    )
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert 'disease' in data
    assert data['disease'] == 'Leafspot'
    assert data['response'] == "This is a response about strawberry diseases."
    
    # Verify Gemini was called with correct parameters
    mock_generate_content.assert_called_once()

def test_chatbot_route_invalid_request(client):
    """Test the chatbot API with invalid request."""
    # Missing fields
    response = client.post(
        '/chatbot',
        json={'message': 'Hello'},
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.model')
def test_realtime_detect_continuous(mock_model, client, mock_yolo_results):
    """Test continuous realtime detection API."""
    # Mock model to return our mocked results
    mock_model.return_value = mock_yolo_results
    
    # Create test image and encode to base64
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    
    # Send request
    response = client.post(
        '/realtime_detect_continuous',
        json={'image': f'data:image/jpeg;base64,{img_base64}'},
        content_type='application/json'
    )
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'detections' in data
    assert len(data['detections']) == 2  # We mocked 2 detections
    
    # Verify model was called
    mock_model.assert_called_once()