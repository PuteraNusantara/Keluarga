from flask import Flask, request, redirect, url_for, render_template_string
import mysql.connector
import os

app = Flask(__name__)

# Konfigurasi database
db_config = {
    'host': 'localhost:3307',
    'user': 'root',  # Ganti dengan username MySQL Anda
    'password': '',  # Ganti dengan password MySQL Anda
    'database': 'galeri_keluarga'
}

# Fungsi untuk menyimpan gambar ke database
def simpan_gambar(nama_file, path_file):
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    query = "INSERT INTO gambar (nama_file, path_file) VALUES (%s, %s)"
    values = (nama_file, path_file)
    cursor.execute(query, values)
    db.commit()
    cursor.close()
    db.close()

# Fungsi untuk mengambil gambar dari database
def ambil_gambar():
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM gambar")
    gambar = cursor.fetchall()
    cursor.close()
    db.close()
    return gambar

# Halaman utama
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'fileInput' not in request.files:
            return redirect(url_for('index'))

        files = request.files.getlist('fileInput')

        for file in files:
            if file.filename == '':
                continue

            # Simpan file ke folder uploads
            upload_folder = 'uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, file.filename)
            file.save(file_path)

            # Simpan informasi gambar ke database
            simpan_gambar(file.filename, file_path)

        return redirect(url_for('index'))

    # Ambil data gambar dari database
    gambar = ambil_gambar()
    return render_template_string('''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Galeri Keluarga</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            background-color: #f4f4f4;
            color: #333;
        }

        header {
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
        }

        main {
            padding: 20px;
        }

        .upload-section {
            margin-bottom: 20px;
            text-align: center;
        }

        .upload-section input {
            display: none;
        }

        .upload-section button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .upload-section button:hover {
            background-color: #45a049;
        }

        .gallery {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
        }

        .gallery-item {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
            width: 200px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            position: relative;
            padding-bottom: 10px;
        }

        .gallery-item img {
            width: 100%;
            height: 150px;
            object-fit: cover;
        }

        .gallery-item p {
            padding: 10px;
            font-size: 14px;
        }

        .download-btn {
            display: inline-block;
            background-color: #2196F3;
            color: white;
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            cursor: pointer;
        }

        .download-btn:hover {
            background-color: #0b7dda;
        }

        footer {
            background-color: #333;
            color: white;
            text-align: center;
            padding: 10px;
            position: fixed;
            bottom: 0;
            width: 100%;
        }
    </style>
</head>
<body>
    <header>
        <h1>Galeri Keluarga</h1>
        <p>Upload dan bagikan kenangan indah bersama keluarga.</p>
    </header>

    <main>
        <!-- Form Upload Gambar -->
        <section class="upload-section">
            <form action="/" method="post" enctype="multipart/form-data">
                <input type="file" id="fileInput" name="fileInput" accept="image/*" multiple>
                <button type="submit" id="uploadButton">Upload Gambar</button>
            </form>
        </section>

        <!-- Galeri Gambar -->
        <section class="gallery">
            {% for item in gambar %}
            <div class="gallery-item">
                <img src="{{ item.path_file }}" alt="{{ item.nama_file }}">
                <p>{{ item.nama_file }}</p>
                <a href="{{ item.path_file }}" download class="download-btn">Download</a>
            </div>
            {% endfor %}
        </section>
    </main>

    <footer>
        <p>&copy; 2023 Galeri Keluarga. Semua hak dilindungi.</p>
    </footer>
</body>
</html>
    ''', gambar=gambar)

if __name__ == '__main__':
    # Pastikan folder uploads ada
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Jalankan aplikasi
    app.run(debug=True)