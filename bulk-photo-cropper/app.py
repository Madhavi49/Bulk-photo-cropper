import os
import zipfile
import io
from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image

app = Flask(__name__)

# --- Configuration ---
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'

# Ensure the folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# 1. Home Page
@app.route('/')
def home():
    # Optional: Clear folders when starting fresh
    return render_template('index.html')

# 2. Upload Logic (Handles multiple files)
@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return redirect(request.url)
    
    files = request.files.getlist('files')
    for file in files:
        if file.filename != '':
            # Save original image
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            
    return redirect(url_for('resize'))

# 3. Resize Page (Displays the Grid)
@app.route('/resize')
def resize():
    # List all files in upload folder to show in the grid
    images = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return render_template('resize.html', images=images)

# 4. Processing Logic (Pixel vs Percentage)
@app.route('/process', methods=['POST'])
def process():
    # mode comes from the hidden input id="modeVal"
    mode = request.form.get('mode', 'pixel') 
    
    # Clear the processed folder from previous runs
    for f in os.listdir(PROCESSED_FOLDER):
        os.remove(os.path.join(PROCESSED_FOLDER, f))

    for filename in os.listdir(UPLOAD_FOLDER):
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            with Image.open(img_path) as img:
                # MODE 1: Pixel based
                if mode == 'pixel':
                    width = int(request.form.get('width', 300))
                    height = int(request.form.get('height', 300))
                    # Fallback if user left it at 0
                    if width <= 0: width = img.width
                    if height <= 0: height = img.height
                
                # MODE 2: Percentage based
                else:
                    percent = int(request.form.get('perc', 50))
                    width = int(img.width * (percent / 100))
                    height = int(img.height * (percent / 100))

                # Actual Resizing
                resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                resized_img.save(os.path.join(PROCESSED_FOLDER, filename))
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    return redirect(url_for('result'))

# 5. Result Page
@app.route('/result')
def result():
    return render_template('result.html')

# 6. Download ZIP Logic
@app.route('/download-all')
def download_all():
    # Create ZIP in memory so we don't clutter the server
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename in os.listdir(PROCESSED_FOLDER):
            file_path = os.path.join(PROCESSED_FOLDER, filename)
            zf.write(file_path, filename)
    
    memory_file.seek(0)
    return send_file(
        memory_file, 
        download_name='resized_images.zip', 
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)