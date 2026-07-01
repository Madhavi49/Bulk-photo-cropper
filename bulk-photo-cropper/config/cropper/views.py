import os
import zipfile
import io

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from PIL import Image

# Folders for uploads and processed images
UPLOAD_FOLDER = os.path.join(settings.BASE_DIR.parent, 'static', 'uploads')
PROCESSED_FOLDER = os.path.join(settings.BASE_DIR.parent, 'static', 'processed')

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def home(request):
    return render(request, 'index.html')


def upload(request):
    if request.method == "POST":
        # Check if this is the first upload from home page
        first_upload = request.POST.get('first_upload', 'yes') == 'yes'

        if first_upload:
            # Clear old uploaded images only if starting fresh
            for f in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, f)
                try:
                    os.remove(file_path)
                except PermissionError:
                    print(f"Skipping locked file: {file_path}")

        # Save new uploaded images
        files = request.FILES.getlist('files')
        for file in files:
            file_path = os.path.join(UPLOAD_FOLDER, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        return redirect('resize')

    return redirect('home')


def resize(request):
    images = [
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    return render(request, 'resize.html', {'images': images})


def process(request):
    if request.method != "POST":
        return redirect('home')

    mode = request.POST.get('mode', 'pixel')

    # Safely clear old processed files
    for f in os.listdir(PROCESSED_FOLDER):
        file_path = os.path.join(PROCESSED_FOLDER, f)
        try:
            os.remove(file_path)
        except PermissionError:
            print(f"Skipping locked file: {file_path}")

    # Process each uploaded image
    for filename in os.listdir(UPLOAD_FOLDER):
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(PROCESSED_FOLDER, filename)

        try:
            with Image.open(img_path) as img:

                if mode == 'pixel':
                    width = int(request.POST.get('width', 300))
                    height = int(request.POST.get('height', 300))
                    if width <= 0: width = img.width
                    if height <= 0: height = img.height
                else:
                    percent = int(request.POST.get('perc', 50))
                    width = int(img.width * percent / 100)
                    height = int(img.height * percent / 100)

                resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                resized_img.save(output_path)
                resized_img.close()

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    return redirect('result')


def result(request):
    return render(request, 'result.html')


def download_all(request):
    """Download all processed images as a single ZIP file."""
    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename in os.listdir(PROCESSED_FOLDER):
            file_path = os.path.join(PROCESSED_FOLDER, filename)
            zf.write(file_path, filename)

    memory_file.seek(0)

    # Return HttpResponse so browser downloads the ZIP
    response = HttpResponse(memory_file.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=resized_images.zip'
    response['Content-Length'] = memory_file.tell()
    return response