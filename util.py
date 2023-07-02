import requests
import cv2
import numpy as np
import pygame
from datetime import datetime

from constants import *

pygame.init()
warning = pygame.mixer.Sound("warning.wav")


def calculate_center(indexes, points, img, draw=False):
    (cx, cy), radius = cv2.minEnclosingCircle(points[indexes])

    center = np.array([cx, cy], dtype=np.int32)

    if draw:
        cv2.circle(img, center, int(radius), (0, 255, 0), 1, cv2.LINE_AA)

    return center


def eye_direction(iris_center, eye_center):
    if abs(iris_center[0] - eye_center[0]) < 5:
        return "CENTER"
    elif iris_center[0] - eye_center[0] < 0:
        return "TURN LEFT"
    elif iris_center[0] - eye_center[0] > 0:
        return "TURN RIGHT"


def warn(img, user_name: str = USER_NAME):
    h, w, c = img.shape
    cv2.rectangle(img, (0, 0), (w, h), (0, 0, 255), -1)
    cv2.putText(
        img,
        "You have lost focus",
        (150, 250),
        cv2.FONT_HERSHEY_PLAIN,
        2,
        (255, 255, 255),
        4,
    )
    cv2.imshow(WINDOW_TITLE, img)
    cv2.waitKey(1)

    # Call the database to add distraction instance
    response = requests.post(
        "http://127.0.0.1:8000/dashboard/add_distraction/",
        params={"name": user_name},
    )

    if response.status_code == 200:
        print("Request inserted into database successfully")
    else:
        print("Request failed with status code:", response.status_code)

    # Play warning sound
    pygame.mixer.Sound.play(warning)

    # Record when the user first loses focus into log.txt
    now = datetime.now()
    cur_time = now.strftime("%d.%m.%Y - %H:%M:%S")

    with open("log.txt", "a") as f:
        f.write(f"{user_name} has lost focus from {cur_time} to ")
