# 👁️‍🗨️ Face Recognition Based Attendance Management System with Power BI

An end-to-end smart attendance solution that integrates **Machine Learning**, **Flask Web Development**, **SQLite3 Database**, and **Power BI** dashboards to detect faces, mark attendance, and visualize data in real time.

---

## 👨‍💻 Developed by: Aaryan M

---

## 🧠 Technologies & Concepts Used

| Domain              | Tools & Concepts                                     |
|---------------------|------------------------------------------------------|
| Machine Learning     | `OpenCV`, `face-recognition`, `dlib`, `HOG`, `Triplet Loss`, `Euclidean Distance` |
| Web Development      | `Flask`, `HTML`, `CSS`, `JavaScript`                |
| Database             | `SQLite3`                                           |
| Data Analytics       | `Power BI`, `CSV Export`, `Trend Analysis`          |
| Programming Language | `Python`                                            |

---

## 🚀 Features

- 🔍 Real-time **face detection and recognition**
- ✅ **Auto attendance logging** with timestamp
- 👨‍💼 **Secure admin login panel**
- 📈 **Interactive dashboards** using **Power BI**
- 📦 Attendance records stored in `SQLite3` and exported as `.csv`
- 📸 Detects **multiple faces simultaneously**
- 🌙 Works in **both bright and low-light** conditions

---

## 📁 Project Structure

📂 face_recognition_attendance_management_with-PowerBI/
├── app.py # Flask web app
├── camera.py # Webcam controller
├── face_recognition_model.py # Core recognition logic
├── database.py # SQLite3 database handler
├── static/
│ └── styles.css # CSS for Flask frontend
├── templates/
│ ├── index.html # Main app interface
│ ├── login.html # Admin login UI
├── attendance/
│ └── attendance.csv # Exported attendance file
├── trained_faces/
│ └── <name>.jpg # Face images of known individuals
├── dashboard/
│ └── attendance_dashboard.pbix # Power BI dashboard file
└── requirements.txt



---

## ⚙️ Methodology
```bash
1. Environment Setup
conda create -n face-env python=3.9
conda activate face-env
pip install -r requirements.txt
2. Face Detection
Convert to grayscale and detect using HOG

Crop and encode faces using face_recognition

3. Face Embedding & Comparison
Generate 128-dimensional embeddings

Use Euclidean distance to compare input face with known encodings

4. Attendance Management
Store attendance in SQLite3

Export attendance to CSV for Power BI

5. Power BI Dashboard
Connect attendance.csv to Power BI

Build visualizations: daily presence, trends, frequency, etc.

(Optional) Embed Power BI report in web interface via iframe

📊 Sample Power BI Dashboard
Total Students Present/Absent

Date-wise Attendance Trends

Most Present/Least Present Students

Dynamic Filters (Date, Time, Names, etc.)

Dashboard file: /dashboard/attendance_dashboard.pbix

🔐 Admin Panel
Secure login with predefined credentials

View attendance

Download CSV

🧪 Sample Output Log
plaintext
Copy
Edit
[INFO] Camera started...
[✔] Recognized: Aaryan M at 09:23:41
[✔] Recognized: Abhishek S at 09:23:47
[✔] CSV Updated — Attendance marked.
💻 How to Run the Project
Step 1: Clone the Repository
bash
Copy
Edit
git clone https://github.com/Aaryan1901/face_recognition_attendance_management_with-PowerBI.git
cd face_recognition_attendance_management_with-PowerBI
Step 2: Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
Step 3: Launch the App
bash
Copy
Edit
python app.py
Open your browser at http://127.0.0.1:5000/

📦 Dataset & Face Training
Add images of known individuals into /trained_faces/

File names should match the person's name (e.g., aaryan.jpg)

On app start, these images are encoded and loaded for face recognition

🛡️ Security
Admin authentication via Flask session

Can be enhanced with hashed passwords + role-based access

🏁 Future Enhancements
Add support for email reports

Auto-refresh live dashboards

Integrate with cloud storage (Firebase or AWS S3)

Add face registration form for new users

Multi-user role support (students, faculty, admin)

📜 License
This project is licensed under the MIT License.

🙌 Connect with Me
📧 Email: aaryan.m299@ptuniv.edu.in

🌐 GitHub: @Aaryan1901

🔗 LinkedIn: Aaryan M

