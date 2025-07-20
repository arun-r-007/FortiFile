from flask import Flask, flash, render_template, request, send_file, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
import os
import uuid
import pymysql
from encrypt_decrypt import encrypt_file, decrypt_file

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
db = pymysql.connect(
    host="localhost",
    user="root",
    password="",        # Mysql Password
    database="cloud4"   # Database Name
)

# Home Route
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with db.cursor() as cursor:
            cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password!", "error")
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    with db.cursor() as cursor:
        cursor.execute("SELECT file_id, filename FROM files WHERE user_id = %s", (user_id,))
        files = cursor.fetchall()
    
    return render_template('dashboard.html', files=files)

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        
        with db.cursor() as cursor:
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("Username already exists. Please choose a different one.", "error")
                return redirect(url_for('register'))

            # Insert new user
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        db.commit()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Upload Route
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        file = request.files['file']
        if file:
            user_id = session['user_id']
            unique_id = str(uuid.uuid4())
            filename = file.filename
            file_content = file.read()
            
            try:
                encrypted_data = encrypt_file(file_content)
            except Exception as e:
                flash(f"An error occurred during encryption: {str(e)}", "error")
                return redirect(url_for('upload_file'))

            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO files (user_id, file_id, filename, encrypted_data)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, unique_id, filename, encrypted_data))
            db.commit()

            flash("File uploaded and encrypted successfully!", "success")
            return redirect(url_for('show_upload_message'))

    return render_template('upload.html')

@app.route('/upload_success')
def show_upload_message():
    return render_template('upload_success.html')

# Download Route
@app.route('/download', methods=['GET', 'POST'])
def download_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file_id = request.form['file_id']
        user_id = session['user_id']

        with db.cursor() as cursor:
            cursor.execute(""" 
                SELECT filename, encrypted_data FROM files 
                WHERE user_id = %s AND file_id = %s 
            """, (user_id, file_id))
            file_data = cursor.fetchone()

        if file_data:
            filename, encrypted_data = file_data
            
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode('latin1')

            try:
                decrypted_data = decrypt_file(encrypted_data)
                return send_file(BytesIO(decrypted_data), as_attachment=True, download_name=filename)
            except Exception as e:
                flash(f"Error decrypting file: {str(e)}", "error")
                return redirect(url_for('dashboard'))
        else:
            flash("File not found or access denied.", "error")
            return redirect(url_for('ret1'))

    return render_template('download.html')

@app.route('/ret')
def ret1():
    return render_template('ret.html')

if __name__ == '__main__':
    app.run(debug=True)
