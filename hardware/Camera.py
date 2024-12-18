# Sources:
# ChatGPT model: OpenAI GPT-4 (03/12/2024)

import cv2
import numpy as np

class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.motion_detected = False

    def detect_motion(self):
        ret, frame1 = self.camera.read()
        ret, frame2 = self.camera.read()
        
        while self.camera.isOpened():
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) < 500:
                    continue
                self.motion_detected = True
                break
            else:
                self.motion_detected = False
            
            frame1 = frame2
            ret, frame2 = self.camera.read()
            
            if not ret:
                break

    def is_motion_detected(self):
        return self.motion_detected

    def release(self):
        self.camera.release()
        cv2.destroyAllWindows()


