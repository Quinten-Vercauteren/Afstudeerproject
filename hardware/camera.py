import cv2
import numpy as np
import time
import os
from hardware import get_filament_weight  # Import the function to get filament weight

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


# Global variables
camera_state = "Inactive"
motion_count = 0
no_motion_start_time = None
motion_start_time = None
state_cooldown = 5  # Cooldown time in seconds
state_file_path = "/tmp/printer_state.txt"  # Path to the temporary file

# Ensure the state file exists
if not os.path.exists(state_file_path):
    with open(state_file_path, "w") as state_file:
        state_file.write(camera_state)


def update_camera_state():
    global camera_state, motion_count, no_motion_start_time, motion_start_time

    stream_url = "http://octoproject.local/webcam/?action=stream"
    camera = Camera(stream_url=stream_url)

    frame_width = int(camera.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Use a compatible codec
    path = "Detected_Motion.MP4"
    out = cv2.VideoWriter(path, fourcc, 30, (frame_width, frame_height))

    last_state_change_time = time.time()
    last_print_time = time.time()

    try:
        # Initialize frames
        ret, CurrentFrame = camera.camera.read()
        ret, NextFrame = camera.camera.read()

        while camera.camera.isOpened():
            if ret:
                # Calculate frame difference
                diff = cv2.absdiff(CurrentFrame, NextFrame)
                gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                blured_img = cv2.GaussianBlur(gray, (5, 5), 0)
                _, binary_img = cv2.threshold(blured_img, 25, 255, cv2.THRESH_BINARY)
                dilated = cv2.dilate(binary_img, None, iterations=8)
                contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

                motion_detected = False
                for contour in contours:
                    contour_area = cv2.contourArea(contour)
                    if contour_area >= 500:
                        motion_detected = True
                        print(f"Detected motion with contour area: {contour_area}")
                        break

                # Motion logic
                current_time = time.time()
                if motion_detected:
                    if motion_start_time is None:
                        motion_start_time = current_time
                    motion_count += 1
                    no_motion_start_time = None
                elif not motion_detected:
                    if no_motion_start_time is None:
                        no_motion_start_time = current_time
                    motion_start_time = None

                # State transitions
                if (
                    motion_count >= 3
                    and motion_start_time is not None
                    and (current_time - motion_start_time) <= 2
                    and camera_state != "Printing"
                ):
                    camera_state = "Printing"
                    motion_count = 0
                    motion_start_time = None
                    last_state_change_time = current_time
                    weight = get_filament_weight()  # Get the current weight
                    print(f"State changed to Printing due to detected motion in the last 2 seconds. Number of contours: {len(contours)}. Current weight: {weight} grams")

                elif (
                    no_motion_start_time
                    and (current_time - no_motion_start_time) >= 60
                    and (current_time - last_state_change_time) >= state_cooldown
                    and camera_state != "Inactive"
                ):
                    camera_state = "Inactive"
                    motion_count = 0
                    no_motion_start_time = None
                    last_state_change_time = current_time
                    weight = get_filament_weight()  # Get the current weight
                    print(f"State changed to Inactive due to no motion detected for 30 seconds. Current weight: {weight} grams")

                # Write the current state to the temporary file
                with open(state_file_path, "w") as state_file:
                    state_file.write(camera_state)

                # Save current frame to output
                out.write(CurrentFrame)
                CurrentFrame = NextFrame
                ret, NextFrame = camera.camera.read()

                # Key press to exit
                if cv2.waitKey(30) == ord("g"):
                    break

                # Print the state every 10 seconds
                if time.time() - last_print_time >= 10:
                    print(f"Current state: {camera_state}")
                    last_print_time = time.time()
            else:
                print("Failed to read frame from camera.")
                break
    except KeyboardInterrupt:
        print("Motion detection stopped.")
    finally:
        camera.release()
        out.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    update_camera_state()
