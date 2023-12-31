import cv2
import mediapipe as mp
import numpy as np
import time
from datetime import datetime
from constants import *
from util import calculate_center, eye_direction, warn

mpFace = mp.solutions.face_mesh

cap = cv2.VideoCapture(1)

face_mesh = mpFace.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.9,
    min_tracking_confidence=0.7,
)

t1 = time.time()
warned = False

while True:
    success, img = cap.read()
    if not success:
        break

    # Process image
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, c = img.shape
    results = face_mesh.process(imgRGB)

    # Find landmarks
    if results.multi_face_landmarks:
        # Find points
        points = np.array(
            [
                np.multiply([p.x, p.y], [w, h]).astype(int)
                for p in results.multi_face_landmarks[0].landmark
            ]
        )

        # Calculate the center point of both irises and eyes
        left_iris_center = calculate_center(LEFT_IRIS, points, img, True)
        right_iris_center = calculate_center(RIGHT_IRIS, points, img, True)

        left_eye_center = calculate_center(LEFT_EYE, points, img)
        right_eye_center = calculate_center(RIGHT_EYE, points, img)

        # Determine the direction the eye is looking and display the text
        eye1 = eye_direction(left_iris_center, left_eye_center)
        eye2 = eye_direction(right_iris_center, right_eye_center)

        if eye1 == eye2:
            direction = eye1
        else:
            direction = eye1 if eye1 != "CENTER" else eye2

        cv2.putText(
            img,
            "DIRECTION: " + direction,
            (10, 450),
            cv2.FONT_HERSHEY_PLAIN,
            3,
            (255, 255, 255),
            2,
        )

        # If user's eyes are not in the center for more than 2 seconds warn them
        if direction == "CENTER":
            t1 = time.time()

            if warned:
                warned = False

                # Record how long user has been distracted into log.txt
                now = datetime.now()
                cur_time = now.strftime("%H:%M:%S")

                with open("log.txt", "a") as f:
                    f.write(cur_time + "\n")

        elif direction != "CENTER" and not warned:
            t2 = time.time()
            if t2 - t1 > 2:
                warn(img, USER_NAME)
                warned = True

    # If face is off the screen for longer than 2 seconds it will warn the user
    else:
        if not warned:
            t2 = time.time()
            if t2 - t1 > 2:
                warn(img, USER_NAME)
                warned = True

    cv2.imshow(WINDOW_TITLE, img)
    cv2.waitKey(1)

    # Click the close button to close window
    if cv2.getWindowProperty(WINDOW_TITLE, cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
