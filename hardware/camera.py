import cv2
import numpy as np
import time
# from flask import Flask, jsonify

# app = Flask(__name__)

class Camera:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.camera = cv2.VideoCapture(self.stream_url)
        if not self.camera.isOpened():
            print(f"Error: Camera stream at {self.stream_url} could not be opened.")
        self.motion_detected = False

    def capture_frame(self):
        ret, frame = self.camera.read()
        if not ret:
            print("Error: Failed to capture frame.")
            return None
        return frame

    def release(self):
        self.camera.release()
        cv2.destroyAllWindows()

camera_state = "inactive"
motion_count = 0
no_motion_start_time = None
motion_start_time = None

def update_camera_state():
    global camera_state, motion_count, no_motion_start_time, motion_start_time

    stream_url = "http://octoproject.local/webcam/?action=stream"  # Replace with your OctoPrint stream URL
    camera = Camera(stream_url=stream_url)
    frame_width = int(camera.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"X264")
    path = "Detected_Motion.MP4"
    out = cv2.VideoWriter(path, fourcc, 30, (frame_width, frame_height))

    last_print_time = time.time()

    try:
        done, CurrentFrame = camera.camera.read()
        done, NextFrame = camera.camera.read()

        while camera.camera.isOpened():
            if done:
                diff = cv2.absdiff(CurrentFrame, NextFrame)
                gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                blured_img = cv2.GaussianBlur(gray, (5, 5), 0)
                threshold, binary_img = cv2.threshold(blured_img, 35, 255, cv2.THRESH_BINARY)
                dilated = cv2.dilate(binary_img, None, iterations=12)
                contours, hierarchy = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

                motion_detected = False
                for contour in contours:
                    (x, y, w, h) = cv2.boundingRect(contour)
                    area = cv2.contourArea(contour)
                    if area >= 500:
                        motion_detected = True

                if motion_detected:
                    if motion_start_time is None:
                        motion_start_time = time.time()
                    motion_count += 1
                    no_motion_start_time = None
                else:
                    if no_motion_start_time is None:
                        no_motion_start_time = time.time()

                if motion_count >= 4 and (time.time() - motion_start_time) <= 2:
                    camera_state = "printing"
                    motion_count = 0
                    motion_start_time = None
                elif no_motion_start_time and (time.time() - no_motion_start_time) >= 30:
                    camera_state = "inactive"
                    motion_count = 0
                    no_motion_start_time = None

                out.write(CurrentFrame)
                CurrentFrame = NextFrame
                done, NextFrame = camera.camera.read()

                if cv2.waitKey(30) == ord("g"):
                    break

                # Print the state every 10 seconds
                if time.time() - last_print_time >= 10:
                    print(f"Current state: {camera_state}")
                    last_print_time = time.time()
            else:
                break
    except KeyboardInterrupt:
        print("Motion detection stopped.")
    finally:
        camera.release()
        out.release()
        cv2.destroyAllWindows()

# @app.route('/printer_state', methods=['GET'])
# def get_printer_state():
#     return jsonify({"state": camera_state})

if __name__ == "__main__":
    # from threading import Thread
    # camera_thread = Thread(target=update_camera_state)
    # camera_thread.start()
    # app.run(host='0.0.0.0', port=5002)
    update_camera_state()