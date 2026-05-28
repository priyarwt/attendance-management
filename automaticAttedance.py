import pandas as pd
import datetime
import cv2
import os
import time
import tkinter as tk
from tkinter import *
import numpy as np
from PIL import Image, ImageTk


base_path = os.path.dirname(os.path.abspath(__file__))

haarcasecade_path = os.path.join(base_path, "haarcascade_frontalface_default.xml")
trainimagelabel_path = os.path.join(base_path, "TrainingImageLabel", "Trainner.yml")
studentdetail_path = os.path.join(base_path, "StudentDetails", "studentdetails.csv")
attendance_path = os.path.join(base_path, "Attendance")

# --- HELPER FUNCTIONS ---
def safe_configure(widget, text):
    """Safely updates a widget's text, preventing crashes if the window is closed."""
    try:
        widget.configure(text=text)
    except:
        print(f"STATUS: {text}")

def mark_attendance(Enrollment, Name, Subject, ts, date, time):
    subject_attendance_dir = os.path.join(attendance_path, Subject)
    os.makedirs(subject_attendance_dir, exist_ok=True)
    
    # The filename will now use the corrected date format (e.g. Subject_26-11-2025.csv)
    csv_file_path = os.path.join(subject_attendance_dir, f"{Subject}_{date}.csv")
    
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Enrollment", "Name"])

    if ts not in df.columns:
        df[ts] = np.nan

    if Enrollment not in df['Enrollment'].values:
        new_row = pd.DataFrame([[Enrollment, Name]], columns=["Enrollment", "Name"])
        df = pd.concat([df, new_row], ignore_index=True)
        
    df.loc[df['Enrollment'] == Enrollment, ts] = 1
    df.to_csv(csv_file_path, index=False)


def recognize_attendace(subject, text_to_speech, mess):
    try:
        if not os.path.exists(trainimagelabel_path):
            safe_configure(mess, "ERROR: Trainer not found. Please train images first.")
            text_to_speech("ERROR: Trainer not found. Please train images first.")
            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(trainimagelabel_path)
        detector = cv2.CascadeClassifier(haarcasecade_path)
        
        df = pd.read_csv(studentdetail_path)
        
    except Exception as e:
        safe_configure(mess, f"Initialization Error: {e}")
        text_to_speech("Initialization failed.")
        return

    ts = time.time()
    # ================= FIX APPLIED HERE =================
    # Changed format to %d-%m-%Y (Day-Month-Year)
    date = datetime.datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
    # ====================================================
    
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    Hour, Minute, Second = timeStamp.split(":")
    ts_col = f"{Hour}-{Minute}-{Second}"

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    text_to_speech(f"Ready to take attendance for {subject}")
    safe_configure(mess, f"Ready to take attendance for {subject}...")
    
    future = time.time() + 20 
    
    while True:
        if time.time() > future:
            break
            
        ret, im = cam.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.2, 5)

        for x, y, w, h in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y : y + h, x : x + w])
            
            if conf < 60:
                try:
                    Enrollment = df.loc[df["Enrollment"] == Id]["Enrollment"].values[0]
                    Name = df.loc[df["Enrollment"] == Id]["Name"].values[0]
                    
                    mark_attendance(Enrollment, Name, subject, ts_col, date, timeStamp)
                    
                    cv2.putText(im, str(Name), (x, y + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    safe_configure(mess, f"Attendance Marked: {Name}")
                    
                except IndexError:
                    cv2.putText(im, "Unknown (DB Missing)", (x, y + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    safe_configure(mess, "Attendance Failed: Face Recognized but DB entry missing")
                
            else:
                cv2.putText(im, "Unknown", (x, y + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                safe_configure(mess, "Attendance Failed: Unknown Face")

        cv2.imshow("Taking Attendance", im)
        
        if cv2.waitKey(1) == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()
    safe_configure(mess, "Attendance process complete. Ready for next action.")
    text_to_speech("Attendance process complete.")


def subjectChoose(text_to_speech):
    subject = Tk()
    subject.title("Subject Selection...")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)

    titl = tk.Label(
        subject,
        text="Which Subject Attendance?",
        bg="black",
        fg="green",
        font=("arial", 25),
    )
    titl.place(x=100, y=12)
    
    mess = tk.Label(
        subject,
        text="",
        width=30,
        height=2,
        bd=5,
        bg="black",
        fg="yellow",
        relief=RIDGE,
        font=("times", 14, "bold"),
    )
    mess.place(x=150, y=250)

    def Attf():
        sub = tx.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
            mess.configure(text=t)
        else:
            try:
                os.startfile(os.path.join(attendance_path, sub))
            except FileNotFoundError:
                t = f"Attendance folder for subject '{sub}' not found."
                text_to_speech(t)
                mess.configure(text=t)

    attf = tk.Button(
        subject,
        text="Check Sheets",
        command=Attf,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=10,
        relief=RIDGE,
    )
    attf.place(x=360, y=170)

    sub_label = tk.Label(
        subject,
        text="Enter Subject",
        width=10,
        height=2,
        bg="black",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 15),
    )
    sub_label.place(x=50, y=100)

    tx = tk.Entry(
        subject,
        width=15,
        bd=5,
        bg="black",
        fg="yellow",
        relief=RIDGE,
        font=("times", 30, "bold"),
    )
    tx.place(x=190, y=100)
    
    def take_attendance_action():
        sub = tx.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
            mess.configure(text=t)
        else:
            # We destroy the 'subject' window before starting recognition
            # to prevent UI conflicts
            subject.destroy()
            recognize_attendace(sub, text_to_speech, mess)

    fill_a = tk.Button(
        subject,
        text="Take Attendance",
        command=take_attendance_action,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    fill_a.place(x=195, y=170)
    
    subject.mainloop()