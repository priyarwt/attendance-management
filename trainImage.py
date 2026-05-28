import csv
import os
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time

def getImagesAndLables(path, detector):
    """
    Traverses the training image directory, extracts faces and IDs.
    
    Args:
        path (str): The path to the TrainingImage directory.
        detector (cv2.CascadeClassifier): The loaded face cascade classifier.
        
    Returns:
        tuple: (list of face images (numpy arrays), list of corresponding IDs)
    """
    
    # List all directories inside the main TrainingImage folder
    imagePaths = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    faceSamples = []
    Ids = []
    
    if not imagePaths:
        print("Warning: TrainingImage directory is empty.")
        return faceSamples, Ids

    for student_folder_path in imagePaths:
        # Extract the Enrollment ID from the folder name (e.g., '101_Priya' -> '101')
        try:
            folder_name = os.path.basename(student_folder_path)
            Enrollment_str = folder_name.split('_')[0]
            ID = int(Enrollment_str)
        except (IndexError, ValueError):
            print(f"Skipping folder '{folder_name}'. Cannot extract numeric Enrollment ID.")
            continue

        # Get all image files inside the student's folder
        image_files = [os.path.join(student_folder_path, f) for f in os.listdir(student_folder_path) if f.endswith('.jpg')]

        for imagePath in image_files:
            # Open the image, convert to grayscale
            pilImage = Image.open(imagePath).convert("L")
            imageNp = np.array(pilImage, "uint8")

            # Detect faces in the image (optional, as images are pre-cropped, but safer)
            faces = detector.detectMultiScale(imageNp)

            for x, y, w, h in faces:
                # Append the face sample and the corresponding ID
                faceSamples.append(imageNp[y:y + h, x:x + w])
                Ids.append(ID)
                
    return faceSamples, Ids


# ===============================================================
# FUNCTION: TrainImage (Main training logic)
# ===============================================================
def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message, text_to_speech):
    
    # FIX: Use cv2.face.LBPHFaceRecognizer_create() which is in opencv-contrib-python
    recognizer = cv2.face.LBPHFaceRecognizer_create() 
    
    # FIX: Use the passed-in haarcasecade_path, not a hardcoded string
    detector = cv2.CascadeClassifier(haarcasecade_path)
    
    # Check if the folder is empty
    if not os.listdir(trainimage_path):
        t = "Please take images first!!"
        text_to_speech(t)
        message.configure(text=t)
        return

    try:
        faces, Ids = getImagesAndLables(trainimage_path, detector)
        
        if not faces:
            t = "Error: No faces detected in the training images. Check camera quality."
            text_to_speech(t)
            message.configure(text=t)
            return

        # Train the model
        recognizer.train(faces, np.array(Ids))
        
        # FIX: Use the passed-in path for saving the Trainner.yml file
        recognizer.write(trainimagelabel_path) 
        
        t = "Image Trained Successfully!!"
        text_to_speech(t)
        message.configure(text=t)
        print(t)
        
    except Exception as e:
        err_msg = f"⚠️ Error during training: {str(e)}"
        text_to_speech("Training failed. Check console for details.")
        message.configure(text=err_msg)
        print(err_msg)