from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageOps
import io
import zipfile
import os

app = Flask(__name__)

@app.route('/process-images', methods=['POST'])
def process_images():
    if 'images' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400

    files = request.files.getlist('images')
    if not files:
        return jsonify({'error': 'Empty file list'}), 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file in files:
            try:
                img = Image.open(file)
                inverted_img = ImageOps.invert(img.convert('RGB'))

                img_io = io.BytesIO()
                inverted_img.save(img_io, format='PNG')
                img_io.seek(0)

                zip_file.writestr(f"inverted_{file.filename}", img_io.read())
            except Exception as e:
                return jsonify({'error': f"Failed to process image {file.filename}: {str(e)}"}), 500

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='processed_images.zip'
    )

@app.route('/process-images-to-pdf', methods=['POST'])
def process_images_to_pdf():
    if 'images' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400

    files = request.files.getlist('images')
    if not files:
        return jsonify({'error': 'Empty file list'}), 400

    images = []
    for file in files:
        try:
            img = Image.open(file).convert("RGB")
            inverted = ImageOps.invert(img)
            images.append(inverted)
        except Exception as e:
            return jsonify({'error': f"Error processing {file.filename}: {str(e)}"}), 500

    if not images:
        return jsonify({'error': 'No valid images to process'}), 400

    # Save all images into a single PDF
    pdf_buffer = io.BytesIO()
    images[0].save(pdf_buffer, format='PDF', save_all=True, append_images=images[1:])
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='processed_images.pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
