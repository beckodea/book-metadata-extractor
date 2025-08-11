from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import io
import tempfile
from metadata_extractor import extract_metadata


app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(tempfile.gettempdir(), 'book_metadata_uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set secret key for session management
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-key-123'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    results = []
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                # Reset file pointer to beginning in case it was read before
                file.seek(0)
                
                # Read the file into memory
                file_data = file.read()
                
                # Create a BytesIO object from the file data
                file_obj = io.BytesIO(file_data)
                file_obj.filename = secure_filename(file.filename)
                
                # Extract metadata
                metadata = extract_metadata(file_obj)
                metadata['filename'] = file.filename
                results.append(metadata)
            except Exception as e:
                results.append({
                    'error': f'Error processing {file.filename}: {str(e)}',
                    'filename': file.filename
                })
    
    return jsonify(results)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
