import os
from flask import Flask, redirect, request, send_file, jsonify
from google.cloud import storage

# Initialize Flask app
app = Flask(__name__)

# Google Cloud Storage bucket name
BUCKET_NAME = "project1-images"

# Initialize Google Cloud Storage client
storage_client = storage.Client()

# Determine the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure the temporary directory exists
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def get_files_list():
    """Helper function to return a list of image files in the bucket."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs()
    files = [blob.name for blob in blobs if blob.name.lower().endswith((".jpeg", ".jpg"))]
    return files

@app.route('/')
def index():
    """Home page with upload form and list of uploaded images."""
    index_html = """
    <form method="post" enctype="multipart/form-data" action="/upload">
      <div>
        <label for="file">Choose file to upload</label>
        <input type="file" id="file" name="form_file" accept="image/jpeg"/>
      </div>
      <div>
        <button>Submit</button>
      </div>
    </form>
    <ul>
    """
    files = get_files_list()  # Get the actual list of files
    for file in files:
        index_html += f"<li><a href=\"/files/{file}\">{file}</a></li>"
    index_html += "</ul>"
    return index_html

@app.route('/upload', methods=["POST"])
def upload():
    """Handle file upload and save to Google Cloud Storage."""
    file = request.files['form_file']
    if file:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file)
        return redirect("/")
    return "No file uploaded", 400

@app.route('/files')
def list_files():
    """List files in the Google Cloud Storage bucket."""
    files = get_files_list()  # Use the helper function
    return jsonify(files)

@app.route('/files/<filename>')
def get_file(filename):
    """Download a file from the Google Cloud Storage bucket."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    if blob.exists(storage_client):
        temp_path = os.path.join(TEMP_DIR, filename)  # Use the absolute temp path
        blob.download_to_filename(temp_path)  # Save temporarily
        return send_file(temp_path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
