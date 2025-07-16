from flask import Flask, render_template, request, session
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, date, timedelta
import sqlite3
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Dictionary to store last seen time for each person
attendance_records = {}

def init_database():
    """Initialize the database with proper schema"""
    conn = sqlite3.connect('information.db')
    cursor = conn.cursor()
    
    # Check if table exists and has all required columns
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Attendance'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        # Check columns
        cursor.execute("PRAGMA table_info(Attendance)")
        columns = [column[1] for column in cursor.fetchall()]
        required_columns = ['Date', 'Name', 'Time', 'Duration', 'BreakTime', 'CallDisctd']
        
        for column in required_columns:
            if column not in columns:
                # Add missing columns
                if column == 'Duration':
                    cursor.execute("ALTER TABLE Attendance ADD COLUMN Duration INTEGER DEFAULT 0")
                elif column == 'BreakTime':
                    cursor.execute("ALTER TABLE Attendance ADD COLUMN BreakTime INTEGER DEFAULT 0")
                elif column == 'CallDisctd':
                    cursor.execute("ALTER TABLE Attendance ADD COLUMN CallDisctd INTEGER DEFAULT 0")
    else:
        # Create new table with all columns
        cursor.execute('''CREATE TABLE Attendance
                         (Date TEXT, Name TEXT, Time TEXT, 
                         Duration INTEGER DEFAULT 0,
                         BreakTime INTEGER DEFAULT 0,
                         CallDisctd INTEGER DEFAULT 0)''')
    
    conn.commit()
    conn.close()

def init_csv_file():
    """Initialize the CSV file with proper headers if it doesn't exist or is corrupted"""
    if not os.path.exists('attendance.csv'):
        with open('attendance.csv', 'w') as f:
            f.write('Date,Name,Duration(Mins),BreakTime,CallDisctd\n')
    else:
        try:
            pd.read_csv('attendance.csv')
        except:
            os.rename('attendance.csv', 'attendance_corrupted_backup.csv')
            with open('attendance.csv', 'w') as f:
                f.write('Date,Name,Duration(Mins),BreakTime,CallDisctd\n')

@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == "POST":
        return render_template('index.html')
    else:
        return "Everything is okay!"

@app.route('/name', methods=['GET', 'POST'])
def name():
    if request.method == "POST":
        name1 = request.form['name1']
        name2 = request.form['name2']

        cam = cv2.VideoCapture(0)
        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            cv2.imshow("Press Space to capture image", frame)

            k = cv2.waitKey(1)
            if k % 256 == 27:
                print("Escape hit, closing...")
                break
            elif k % 256 == 32:
                img_name = name1 + ".png"
                path = r'C:\Users\Aaryan\Music\face-recognition-attendance-management-system-with-PowerBI-dashboard\Training images'
                cv2.imwrite(os.path.join(path, img_name), frame)
                print("{} written!".format(img_name))
        cam.release()
        cv2.destroyAllWindows()
        return render_template('image.html')
    else:
        return 'All is not well'

@app.route("/", methods=["GET", "POST"])
def recognize():
    if request.method == "POST":
        path = 'Training images'
        images = []
        classNames = []
        myList = os.listdir(path)
        for cl in myList:
            curImg = cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])
        
        def findEncodings(images):
            encodeList = []
            for img in images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encoded_face = face_recognition.face_encodings(img)
                if len(encoded_face) > 0:
                    encodeList.append(encoded_face[0])
            return encodeList

        def markData(name):
            today = date.today().strftime('%Y-%m-%d')
            now = datetime.now()
            time_str = now.strftime('%H:%M:%S')
            
            # Calculate duration
            duration = 0
            if name in attendance_records:
                duration = int((now - attendance_records[name]).total_seconds() / 60)
                duration = max(1, duration)  # At least 1 minute
            
            conn = sqlite3.connect('information.db')
            cursor = conn.cursor()
            
            # Check if record exists for today
            cursor.execute("SELECT * FROM Attendance WHERE Date=? AND Name=?", (today, name))
            existing_record = cursor.fetchone()
            
            if existing_record:
                # Update existing record
                cursor.execute('''UPDATE Attendance 
                                SET Time=?, Duration=Duration+?, BreakTime=?, CallDisctd=?
                                WHERE Date=? AND Name=?''',
                             (time_str, duration, 0, 0, today, name))
            else:
                # Insert new record
                cursor.execute('''INSERT INTO Attendance 
                                (Date, Name, Time, Duration, BreakTime, CallDisctd)
                                VALUES (?, ?, ?, ?, ?, ?)''',
                             (today, name, time_str, duration, 0, 0))
            
            conn.commit()
            conn.close()

        def markAttendance(name):
            today = date.today().strftime('%Y-%m-%d')
            now = datetime.now()
            time_str = now.strftime('%H:%M:%S')
            
            # Calculate duration
            duration = 0
            if name in attendance_records:
                duration = int((now - attendance_records[name]).total_seconds() / 60)
                duration = max(1, duration)
            
            # Update last seen time
            attendance_records[name] = now
            
            # Initialize CSV file if needed
            init_csv_file()
            
            # Read existing data
            try:
                df = pd.read_csv('attendance.csv')
            except (pd.errors.EmptyDataError, pd.errors.ParserError):
                df = pd.DataFrame(columns=['Date', 'Name', 'Duration(Mins)', 'BreakTime', 'CallDisctd'])
            
            # Update or add record
            mask = (df['Date'] == today) & (df['Name'] == name)
            if not df.empty and mask.any():
                df.loc[mask, 'Duration(Mins)'] += duration
            else:
                new_record = pd.DataFrame([{
                    'Date': today,
                    'Name': name,
                    'Duration(Mins)': duration,
                    'BreakTime': 0,
                    'CallDisctd': 0
                }])
                df = pd.concat([df, new_record], ignore_index=True)
            
            # Save back to CSV
            df.to_csv('attendance.csv', index=False)

        encodeListKnown = findEncodings(images)
        cap = cv2.VideoCapture(0)
        
        while True:
            success, img = cap.read()
            if not success:
                break
                
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
            
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)
                
                if matches[matchIndex] and faceDis[matchIndex] < 0.50:
                    name = classNames[matchIndex].upper()
                    markAttendance(name)
                    markData(name)
                else:
                    name = 'Unknown'
                
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            
            cv2.imshow('Attendance System', img)
            if cv2.waitKey(1) == 27:
                break
                
        cap.release()
        cv2.destroyAllWindows()
        return render_template('first.html')
    else:
        return render_template('main.html')



@app.route('/login', methods=['POST'])
def login():
    json_data = json.loads(request.data.decode())
    username = json_data['username']
    password = json_data['password']
    df = pd.read_csv('cred.csv')
    if len(df.loc[df['username'] == username]['password'].values) > 0:
        if df.loc[df['username'] == username]['password'].values[0] == password:
            session['username'] = username
            return 'success'
        else:
            return 'failed'
    else:
        return 'failed'

@app.route('/checklogin')
def checklogin():
    if 'username' in session:
        return session['username']
    return 'False'

@app.route('/how', methods=["GET", "POST"])
def how():
    return render_template('form.html')

@app.route('/data', methods=["GET", "POST"])
def data():
    if request.method == "POST":
        today = date.today().strftime('%Y-%m-%d')
        conn = sqlite3.connect('information.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cursor = cur.execute("SELECT DISTINCT NAME, Time, Date, Duration, BreakTime, CallDisctd FROM Attendance WHERE Date=?", (today,))
        rows = cur.fetchall()
        conn.close()
        
        # Also get CSV data
        csv_data = []
        if os.path.exists('attendance.csv'):
            df = pd.read_csv('attendance.csv')
            csv_data = df[df['Date'] == today].to_dict('records')
        
        return render_template('form2.html', rows=rows, csv_data=csv_data)
    else:
        return render_template('form1.html')

@app.route('/whole', methods=["GET", "POST"])
def whole():
    conn = sqlite3.connect('information.db')
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor() 
    cursor = cur.execute("SELECT DISTINCT NAME, Time, Date, Duration, BreakTime, CallDisctd FROM Attendance")
    rows = cur.fetchall()
    conn.close()
    
    # Also get all CSV data
    csv_data = []
    if os.path.exists('attendance.csv'):
        df = pd.read_csv('attendance.csv')
        csv_data = df.to_dict('records')
    
    return render_template('form3.html', rows=rows, csv_data=csv_data)

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    # Read CSV data for dashboard
    if os.path.exists('attendance.csv'):
        df = pd.read_csv('attendance.csv')
        # Convert to list of dictionaries for template
        records = df.to_dict('records')
        # Calculate summary statistics
        summary = {
            'total_entries': len(df),
            'unique_names': df['Name'].nunique(),
            'total_duration': df['Duration(Mins)'].sum(),
            'avg_duration': df['Duration(Mins)'].mean()
        }
    else:
        records = []
        summary = {}
    
    return render_template('dashboard.html', records=records, summary=summary)

if __name__ == '__main__':
    init_database()  # Initialize database schema at startup
    init_csv_file()  # Initialize CSV file at startup
    app.run(debug=True)