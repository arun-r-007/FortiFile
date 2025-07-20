# 🔐 Secure File Upload and Download System

This project is a secure web application built with **Flask**, allowing users to **register**, **login**, **upload**, and **download encrypted files**. It uses a **hybrid encryption scheme** combining **RSA** and **AES (Fernet)** to ensure file confidentiality and user data protection.

---

## 📁 Features

* ✅ User Registration and Authentication (Password Hashed using `werkzeug.security`)
* 🔒 File Upload with Hybrid Encryption (RSA for key encryption + AES for file content)
* 🔓 Secure File Download with Decryption
* 📦 File Storage in MySQL as BLOB
* 🧾 Session-based Access Control
* 🌐 HTML Templates (login, register, dashboard, upload, download, success, etc.)

---

## 🧰 Technologies Used

| Tech Stack       | Description                             |
| ---------------- | --------------------------------------- |
| **Flask**        | Web framework                           |
| **PyMySQL**      | MySQL database connector                |
| **Werkzeug**     | Password hashing utilities              |
| **RSA**          | Asymmetric encryption                   |
| **Fernet (AES)** | Symmetric encryption via `cryptography` |
| **MySQL**        | Relational database                     |
| **HTML/CSS**     | Frontend templates                      |

---

## 🔐 How Encryption Works

* A **random Fernet key** is generated for each uploaded file.
* File content is encrypted using Fernet (**AES encryption**).
* The Fernet key is then encrypted using the **user’s public RSA key**.
* Both encrypted key and data are stored together in the database.
* During download, the key is decrypted using the private RSA key and used to decrypt the file.

---

## 🧪 Folder Structure

```
project/
│
├── app.py                      # Main Flask app
├── encrypt_decrypt.py         # RSA + AES encryption logic
├── templates/                 # HTML files
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── download.html
│   ├── upload_success.html
│   └── ret.html
├── public.pem                 # RSA Public Key
├── private.pem                # RSA Private Key
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. 🔧 Prerequisites

* Python 3.x
* MySQL Server
* `pip3` installed

### 2. 📦 Install Dependencies

```bash
pip3 install flask pymysql cryptography rsa
```

### 3. 🛠️ Database Setup

Create a MySQL database named `cloud4`:

```sql
CREATE DATABASE cloud4;

USE cloud4;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_id VARCHAR(100) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    encrypted_data LONGBLOB NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 4. 🔑 Generate RSA Keys

Run this once to generate RSA key pair:

```bash
python encrypt_decrypt.py
```

### 5. 🚀 Run the Flask App

```bash
python app.py
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## 🧩 Key Flask Routes

| Route             | Function                    |
| ----------------- | --------------------------- |
| `/`               | Home page                   |
| `/login`          | Login page                  |
| `/register`       | User registration           |
| `/dashboard`      | File list of logged-in user |
| `/upload`         | Upload + encrypt a file     |
| `/download`       | Download + decrypt a file   |
| `/logout`         | Logout current session      |
| `/upload_success` | Upload success message page |
| `/ret`            | Return/fallback page        |

---

## ⚠️ Security Notes

* RSA keys are stored as PEM files (`public.pem` and `private.pem`). In production, these should be stored securely.
* Sessions use a hardcoded `secret_key` — update it to a secure, random string for production.
* Passwords are hashed but not salted uniquely per user — consider salting for improved security.
