import csv
import os
import cv2
import numpy as np
import pandas as pd
import datetime
import time


def TakeImage(l1, l2, haarcasecade_path, trainimage_path, message, err_screen, text_to_speech):
    if (l1 == "") and (l2 == ""):
        t = "Please Enter your Enrollment Number and Name."
        text_to_speech(t)
        # Assuming 'message' is the widget to show general messages
        message.configure(text="Please Enter your Enrollment Number and Name.")
        return
    elif l1 == "":
        t = "Please Enter your Enrollment Number."
        text_to_speech(t)
        message.configure(text="Please Enter your Enrollment Number.")
        return
    elif l2 == "":
        t = "Please Enter your Name."
        text_to_speech(t)
        message.configure(text="Please Enter your Name.")
        return

    try:
        # Initialize webcam
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            text_to_speech("Error: Cannot access the webcam.")
            message.configure(text="Error: Cannot access the webcam.")
            return

        detector = cv2.CascadeClassifier(haarcasecade_path)
        Enrollment = l1.strip()
        Name = l2.strip()
        sampleNum = 0
        directory = f"{Enrollment}_{Name}"
        path = os.path.join(trainimage_path, directory)

        # Create directory for new student
        os.makedirs(path, exist_ok=True)

        print("📸 Capturing images. Look at the camera... Press 'Q' to stop early.")

        while True:
            ret, img = cam.read()
            if not ret:
                print(" Failed to capture frame from camera.")
                break

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sampleNum += 1
                filename = f"{path}/{Name}_{Enrollment}_{sampleNum}.jpg"
                cv2.imwrite(filename, gray[y:y + h, x:x + w])
                cv2.imshow("Frame", img)

            # Press Q or collect 50 samples
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Stopped by user.")
                break
            elif sampleNum >= 50:
                print(" Image capture complete.")
                break

        cam.release()
        cv2.destroyAllWindows()

        # Save details in CSV file
        row = [Enrollment, Name]
        with open("StudentDetails/studentdetails.csv", "a+", newline="") as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)

        res = f"Images Saved for ER No: {Enrollment}  Name: {Name}"
        message.configure(text=res)
        text_to_speech(res)
        print(res)

    except Exception as e:
        err_msg = f" Error: {str(e)}"
        print(err_msg)
        text_to_speech("An error occurred while capturing images.")
        
       
        if err_screen and hasattr(err_screen, 'configure'):
            err_screen.configure(text=err_msg)
        elif hasattr(message, 'configure'):
             message.configure(text=err_msg)
        # ------------------------


# ===============================================================
# STANDALONE TEST BLOCK (for direct execution)
# ===============================================================
if __name__ == "__main__":
    # Simple test mode to check camera + capture
    def dummy_speak(text):
        print("TTS:", text)

    class DummyMsg:
        def configure(self, text):
            print("MSG:", text)

    haarcascade_path = "haarcascade_frontalface_default.xml"
    trainimage_path = "TrainingImage"

    if not os.path.exists(haarcascade_path):
        print(" Haarcascade file not found. Please place 'haarcascade_frontalface_default.xml' in this folder.")
    else:
        TakeImage(
            l1="101",
            l2="Priya",
            haarcasecade_path=haarcascade_path,
            trainimage_path=trainimage_path,
            message=DummyMsg(),
            err_screen=None,
            text_to_speech=dummy_speak
        )