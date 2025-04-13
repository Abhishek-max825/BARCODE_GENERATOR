from flask import Flask, render_template, request, send_file, url_for, send_from_directory
import barcode
from barcode.writer import ImageWriter
import os
from werkzeug.utils import secure_filename
import zipfile
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/barcodes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class BarcodeGenerator:
    def generate_barcode(self, data, filename):
        code = barcode.get('code128', data, writer=ImageWriter())
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        code.save(filepath)
        return f"{filename}.png"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        count = int(request.form.get('count', 1))
        prefix = request.form.get('prefix', 'BARCODE')
        
        if count < 1 or count > 100:  # Limit to 100 barcodes
            return "Please enter a number between 1 and 100", 400
        
        barcode_files = []
        for i in range(1, count + 1):
            data = f"{prefix}{i}"
            filename = secure_filename(data)
            generator = BarcodeGenerator()
            barcode_file = generator.generate_barcode(data, filename)
            barcode_files.append((barcode_file, data))
        
        return render_template('result.html', 
                             barcode_files=barcode_files,
                             count=count)
    except ValueError:
        return "Please enter a valid number", 400

@app.route('/download')
def download():
    try:
        # Create a zip file in memory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                if filename.endswith('.png'):
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    zf.write(file_path, filename)
        
        memory_file.seek(0)
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='barcodes.zip'
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)