from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
import os
import time
import json
import amaas.grpc

# Initialize Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Fetch API Key and Region from environment variables
API_KEY = os.getenv("VISION_ONE_API_KEY")
REGION = os.getenv("VISION_ONE_REGION", "us-east-1")  # Default to "us-east-1"

# Ensure API key is set
if not API_KEY:
    raise ValueError("VISION_ONE_API_KEY environment variable is not set!")


# Create an AMaaS handle object
try:
    handle = amaas.grpc.init_by_region(region=REGION, api_key=API_KEY)
except Exception as err:
    print(f"Error initializing AMaaS handle: {err}")

# HTML template with Bootstrap 4 and FontAwesome, updated colors based on the image provided
HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>File Upload</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet">
    <style>
      body {
        background-color: #2b2b2b; /* Dark background */
        color: #fff;
        padding-top: 50px;
      }
      .container {
        max-width: 600px;
        background-color: #424242; /* Gray container */
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        color: white; /* White text */
      }
      h1 {
        font-size: 1.75rem;
        color: white; /* White text */
        margin-bottom: 20px;
      }
      label {
        color: white; /* White label text */
      }
      .form-control-file {
        padding: 10px;
        font-size: 1rem;
        background-color: #2e2e2e; /* Darker background for input */
        border: 1px solid #555;
        color: white; /* White text for file input */
        border-radius: 5px;
      }
      .btn {
        background-color: #28a745; /* Green button */
        color: white;
        border: none;
        width: 100%;
      }
      .btn:hover {
        background-color: #218838;
      }
      .alert {
        margin-top: 20px;
        border-radius: 5px;
      }
      .alert-danger {
        background-color: #dc3545;
        color: #fff;
      }
      .alert-success {
        background-color: #28a745;
        color: #fff;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1 class="text-center"><i class="fas fa-upload"></i> Upload Your File</h1>
      <form action="/upload" method="post" enctype="multipart/form-data">
        <div class="form-group">
          <label for="fileInput">Choose file:</label>
          <input type="file" class="form-control-file" id="fileInput" name="file" required>
        </div>
        <button type="submit" class="btn"><i class="fas fa-cloud-upload-alt"></i> Upload</button>
      </form>
      {% if message %}
      <div class="alert alert-info mt-3" role="alert">
        {{ message | safe }}
      </div>
      {% endif %}
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template_string(HTML_TEMPLATE, message='<div class="alert alert-warning">No file part.</div>'), 400
    file = request.files['file']
    if file.filename == '':
        return render_template_string(HTML_TEMPLATE, message='<div class="alert alert-warning">No selected file.</div>'), 400
    if file:
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save the file temporarily for scanning
        file.save(temp_path)

        # Scan the file using Trend Micro Vision One SDK
        try:
            start_time = time.perf_counter()
            response = amaas.grpc.scan_file(handle, file_name=temp_path, pml=None, tags=None)
            elapsed = time.perf_counter() - start_time
            print(f"Scan executed in {elapsed:0.2f} seconds.")

            # Parse the JSON response
            result = json.loads(response) if isinstance(response, str) else response

            # Check the scan result for malware
            if result.get("foundMalwares"):
                malwares = result.get("foundMalwares")
                malware_names = [malware.get("malwareName") for malware in malwares]
                os.remove(temp_path)  # Remove the file if it contains malware

                # Construct the improved message
                message = f"""
                <div class="alert alert-danger">
                    <h4><i class="fas fa-exclamation-triangle"></i> File upload blocked.</h4>
                    <p><strong>Reason:</strong> The uploaded file contains one or more types of malware.</p>
                    <p><strong>Detected malware:</strong> {", ".join(malware_names)}</p>
                    <p><strong>File name:</strong> {filename}</p>
                    <p>Please contact IT support for assistance, or try uploading a clean version of the file.</p>
                </div>
                """
                return render_template_string(HTML_TEMPLATE, message=message)

            else:
                return render_template_string(HTML_TEMPLATE, message=f'''
                    <div class="alert alert-success">
                        <h4><i class="fas fa-check-circle"></i> File successfully uploaded. Thank you!</h4>
                    </div>
                ''')

        except Exception as e:
            print(f"Error scanning file: {e}")
            return render_template_string(HTML_TEMPLATE, message='<div class="alert alert-danger">An error occurred while scanning the file.</div>')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

