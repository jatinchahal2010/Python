from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory
import os

app = Flask(__name__)

# Define upload directory in Termux home
UPLOAD_FOLDER = os.path.expanduser("~/hi/uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Upload & Re-Upload</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container mt-5">
    <h1 class="text-center">Upload and Re-Upload Files</h1>

    <!-- File Upload Form -->
    <form action="{{ url_for('upload_file') }}" method="post" enctype="multipart/form-data" class="mt-4">
        <div class="input-group">
            <input type="file" name="file" class="form-control" required>
            <button type="submit" class="btn btn-primary">Upload</button>
        </div>
    </form>

    <!-- File List -->
    <h2 class="mt-5">Uploaded Files</h2>
    <ul class="list-group">
        {% for file in files %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
                <a href="{{ url_for('uploaded_file', filename=file) }}" target="_blank">{{ file }}</a>
                <a href="{{ url_for('reupload_file', filename=file) }}" class="btn btn-warning btn-sm">Re-Upload</a>
            </li>
        {% endfor %}
    </ul>

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

    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/reupload/<filename>')
def reupload_file(filename):
    original_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(original_path):
        new_path = os.path.join(UPLOAD_FOLDER, f"reuploaded_{filename}")
        os.rename(original_path, new_path)  # Rename to simulate re-upload
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
