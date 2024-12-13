# Sources:
# ChatGPT model: OpenAI GPT-4 (03/12/2024)
# OpenCV library: https://opencv.org/
# NumPy library: https://numpy.org/

'''
import cv2
import numpy as np

# Configuratie
DETECT_THRESHOLD = 50
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 10

def detect_motion(frame1, frame2):
    """Detecteer beweging tussen twee frames."""
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return sum(cv2.contourArea(c) for c in contours) > DETECT_THRESHOLD

def start_camera(camera_id=0):
    """Start de camera en retourneert de capture-object."""
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)
    if not cap.isOpened():
        raise Exception("Kan camera niet openen!")
    return cap
'''