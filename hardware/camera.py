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

    def capture_frame(self):
        ret, frame = self.camera.read()
        if not ret:
            print("Error: Failed to capture frame.")
            return None
        return frame

    def release(self):
        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    stream_url = "http://octoproject.local/webcam/?action=stream"  # Replace with your OctoPrint stream URL
    camera = Camera(stream_url=stream_url)
    frame_width = int(camera.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"X264")
    path = "Detected_Motion.MP4"
    out = cv2.VideoWriter(path, fourcc, 30, (frame_width, frame_height))

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

                for contour in contours:
                    (x, y, w, h) = cv2.boundingRect(contour)
                    area = cv2.contourArea(contour)
                    print(f"Contour at x:{x}, y:{y}, width:{w}, height:{h}, area:{area}")
                    if area >= 1000:
                        cv2.rectangle(CurrentFrame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Log frame processing instead of displaying it
                print("Processed a frame with contours.")

                out.write(CurrentFrame)
                CurrentFrame = NextFrame
                done, NextFrame = camera.camera.read()

                if cv2.waitKey(30) == ord("g"):
                    break
            else:
                break
    except KeyboardInterrupt:
        print("Motion detection stopped.")
    finally:
        camera.release()
        out.release()
        cv2.destroyAllWindows()