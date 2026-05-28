import requests
import cv2
import numpy as np

# Change this URL to the exact one provided by your IP Webcam app
# (e.g., http://192.168.x.x:8080/shot.jpg)
url = "http://192.168.0.6:8080/shot.jpg"

while True:
    try:
        # 1. Fetch the image data from the URL
        cam = requests.get(url)
        
        # 2. Convert the fetched bytes into a numpy array (image data)
        imgNp = np.array(bytearray(cam.content), dtype=np.uint8)
        
        # 3. Decode the numpy array into an OpenCV image format
        img = cv2.imdecode(imgNp, -1)
        
        # 4. Display the image
        cv2.imshow("IP Webcam Feed", img)
        
    except requests.exceptions.RequestException as e:
        # Handle connection errors (e.g., phone disconnected or app closed)
        print(f"Error connecting to webcam: {e}")
        break
    except Exception as e:
        # Handle other errors
        print(f"An error occurred: {e}")
        break

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()