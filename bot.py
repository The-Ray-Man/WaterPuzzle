import pyautogui
import time
import cv2
import numpy as np
import os

os.environ['PATH'] = '/bin'


def do_move(move_description, pos_glasses):
    src, dst = move_description
    cmd = f"adb shell input tap {pos_glasses[src][0]} {pos_glasses[src][1]}"
    os.system(cmd)
    # pyautogui.click(x=pos_glasses[src][0], y=pos_glasses[src][1])
    time.sleep(0.5)
    cmd = f"adb shell input tap {pos_glasses[dst][0]} {pos_glasses[dst][1]}"
    os.system(cmd)
    # pyautogui.click(x=pos_glasses[dst][0], y=pos_glasses[dst][1])
    time.sleep(2)


def bot(move_description, pos_glasses):
    for move in move_description:
        do_move(move, pos_glasses)
    print("Solved")


def playagain():
    os.environ['PATH'] = '/bin'

    os.system("adb exec-out screencap -p > pic.png")

    image = cv2.imread("pic.png",cv2.COLOR_RGB2BGR)

    method = cv2.TM_SQDIFF_NORMED
    small_image = cv2.imread("./playbutton.png")

    result = cv2.matchTemplate(small_image, image, method)

    # We want the minimum squared difference
    mn, _, mnLoc, _ = cv2.minMaxLoc(result)

    # Draw the rectangle:
    # Extract the coordinates of our best match
    MPx, MPy = mnLoc

    # Step 2: Get the size of the template. This is the same size as the match.
    trows, tcols = small_image.shape[:2]
    pyautogui.moveTo(x=MPx + tcols // 2, y=MPy + trows // 2)
    time.sleep(1)
    cmd = f"adb shell input tap {pos_glasses[src][0]} {pos_glasses[src][1]}"
    os.system(cmd)
    time.sleep(3)
