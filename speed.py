from flask import Flask, request, render_template_string, redirect, url_for, send_file, Response
import os
import mimetypes
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Define upload directory in /sdcard/upload/
UPLOAD_FOLDER = "/sdcard/upload"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fast File Upload & Download</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body { background-color: #f8f9fa; }
        .container { max-width: 600px; margin-top: 50px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }
        h1 { text-align: center; color: #007bff; }
        .btn-custom { width: 100%; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Fast File Upload & Download</h1>
        <div class="d-grid gap-2">
            <a href="#upload-section" class="btn btn-primary btn-custom">Upload File</a>
            <a href="#file-list" class="btn btn-success btn-custom">Download Files</a>
        </div>

        <div id="upload-section" class="mt-4">
            <h2>Upload File</h2>
            <form action="{{ url_for('upload_file') }}" method="post" enctype="multipart/form-data">
                <div class="input-group">
                    <input type="file" name="file" class="form-control" required>
                    <button type="submit" class="btn btn-primary">Upload</button>
                </div>
            </form>
        </div>

        <div id="file-list" class="mt-5">
            <h2>Uploaded Files</h2>
            <ul class="list-group">
                {% for file in files %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <span>{{ file }}</span>
                        <a href="{{ url_for('download_file', filename=file) }}" class="btn btn-success btn-sm">Download</a>
                    </li>
                {% endfor %}
            </ul>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Speed optimized file saving
    with open(file_path, "wb") as f:
        for chunk in file.stream:
            f.write(chunk)

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        mimetype, _ = mimetypes.guess_type(file_path)
        return send_file(file_path, as_attachment=True, mimetype=mimetype)

    return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)	
