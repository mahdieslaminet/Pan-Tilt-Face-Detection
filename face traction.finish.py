import cv2
import time
import requests
import numpy as np
import traceback
from serial import Serial, SerialException
from cvzone.FaceDetectionModule import FaceDetector

# Set your Arduino's serial port and baud rate
serial_port = 'COM5'  # Change this to your Arduino's serial port
baud_rate = 9600  # Make sure it matches the baud rate in your Arduino code

camera_url = 'http://192.168.41.25/capture'
detector = FaceDetector()

arduino = None  # Initialize arduino variable

try:
    arduino = Serial(serial_port, baud_rate, timeout=1)
except SerialException as e:
    print(f"Serial Exception: {e}")
    exit()
except Exception as e:
    print(f"Error: {e}")
    exit()

flag = 0
no_face_time = 0.0

while True:
    try:
        response = requests.get(camera_url)
        img_arr = np.array(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, -1)

        img, bboxs = detector.findFaces(img)

        if bboxs:
            face = bboxs[0]  # Assuming only one face is detected

            face_bbox = face['bbox']  # Access the 'bbox' key in the face dictionary

            face_center_x = (face_bbox[0] + int ((face_bbox[2]) / 2 + 0.5))
            face_center_y = (face_bbox[1] + int ((face_bbox[3]) / 2 + 0.5))

            frame_height, frame_width, _ = img.shape
            CENTER_X = int((frame_width) / 2 + 0.5)
            CENTER_Y = int((frame_height) / 2 + 0.5)

            cv2.line(img, (CENTER_X, CENTER_Y), (face_center_x, face_center_y), (0, 255, 0), 2)

            diff_x = face_center_x - CENTER_X
            diff_y = face_center_y - CENTER_Y


            if (CENTER_X - 20 < face_center_x < CENTER_X + 20) and (CENTER_Y - 20 < face_center_y < CENTER_Y + 20):
                pass  # If face is in the dead zone, do nothing
            else:
                if flag == 0:
                    no_face_time = time.time()  # Record the time when no face is detected
                    flag = 1
                if face_center_y < frame_height / 2 + 0.5 and diff_y:
                    diff_y = 0
                    arduino.write(b'u')  # Move tilt up
                elif face_center_y > frame_height / 2 + 0.5 and diff_y:
                    diff_y = 0
                    arduino.write(b'd')  # Move tilt down

                if face_center_x < frame_width / 2 + 0.5 and diff_x:
                    diff_x = 0
                    arduino.write(b'l')  # Move pan left
                elif face_center_x > frame_width / 2 + 0.5 and diff_x:
                    diff_x = 0
                    arduino.write(b'r')  # Move pan right

        else:
            if time.time() - no_face_time >= 5:  # Check if 2 seconds have passed
                arduino.write(b's')  # Move to default position
                print("No face detected.")
                flag = 0  # Reset flag
                no_face_time = 0.0  # Reset no_face_time

        cv2.imshow("image", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except IndexError:
        print("No face detected.")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Type: {type(e)}")
        print(traceback.format_exc())
        break

if arduino:
    arduino.close()
cv2.destroyAllWindows()