# Sources:
# ChatGPT model: OpenAI GPT-4 (03/12/2024)

import cv2
import numpy as np
import time

class Camera:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.camera = cv2.VideoCapture(self.stream_url)
        if not self.camera.isOpened():
            print(f"Error: Camera stream at {self.stream_url} could not be opened.")
        self.motion_detected = False
        self.motion_start_time = None
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)

    def detect_motion(self):
        ret, frame = self.camera.read()
        if not ret:
            print("Error: Failed to capture frame.")
            return False
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)
        
        # Threshold the foreground mask to create a binary image
        _, thresh = cv2.threshold(fg_mask, 25, 255, cv2.THRESH_BINARY)
        
        # Dilate the binary image to fill in gaps
        dilated = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours in the dilated image
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check the areas of the contours to detect motion
        motion_detected = False
        for contour in contours:
            area = cv2.contourArea(contour)
            print(f"Contour area: {area}")
            if area < 500:
                continue
            motion_detected = True
            break
        
        if motion_detected:
            if not self.motion_detected:
                self.motion_start_time = time.time()
            self.motion_detected = True
        else:
            self.motion_detected = False
            self.motion_start_time = None

        return self.motion_detected

    def is_motion_detected(self):
        return self.motion_detected

    def capture_image(self):
        ret, frame = self.camera.read()
        if ret:
            filename = f"capture_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Image captured: {filename}")
        else:
            print("Error: Failed to capture image.")

    def release(self):
        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    stream_url = "http://octoproject.local/webcam/?action=stream"  # Replace with your OctoPrint stream URL
    camera = Camera(stream_url=stream_url)
    if camera.camera.isOpened():
        print(f"Camera stream at {stream_url} opened successfully.")
        try:
            last_print_time = time.time()
            while True:
                motion_detected = camera.detect_motion()
                current_time = time.time()
                if motion_detected:
                    if camera.motion_start_time and (current_time - camera.motion_start_time) > 1:
                        print("Motion detected!")
                else:
                    if (current_time - last_print_time) > 10:
                        print("Waiting for motion")
                        last_print_time = current_time
                time.sleep(1)  # Wait for 1 second before checking again
        except KeyboardInterrupt:
            print("Motion detection stopped.")
        finally:
            camera.release()
    else:
        print(f"Camera stream at {stream_url} could not be opened.")


