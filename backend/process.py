from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import shutil  # For removing files and directories

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Folder paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_files():
    """API to upload Price.xlsx and usage files."""
    try:
        # Clear the uploads folder before saving new files
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        files = request.files.getlist('files')
        if not files:
            return jsonify({"error": "No files provided"}), 400

        # Save uploaded files to the uploads folder
        for file in files:
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))

        return jsonify({"message": "Files uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process', methods=['POST'])
def process_files():
    """API to trigger processing by running app.py."""
    try:
        # Run app.py as a subprocess
        result = subprocess.run(
            ['python3', os.path.join(BASE_DIR, 'app.py')],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        return jsonify({
            "message": "Processing completed",
            "summary_output": "/download/Summary_Output.xlsx",
            "detailed_output": "/download/Detailed_Output.xlsx"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """API to download output files."""
    try:
        return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"File not found: {filename}"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5002)
