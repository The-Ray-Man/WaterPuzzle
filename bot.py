import pyautogui
import time
import cv2
import numpy as np
import os

os.environ['PATH'] = 'C:/Program Files/platform-tools/'


def do_move(move_description, pos_glasses):
    src, dst, anz = move_description
    cmd = f"adb shell input tap {pos_glasses[src][0]} {pos_glasses[src][1]}"
    os.system(cmd)
    # pyautogui.click(x=pos_glasses[src][0], y=pos_glasses[src][1])
    time.sleep(0.25)
    cmd = f"adb shell input tap {pos_glasses[dst][0]} {pos_glasses[dst][1]}"
    os.system(cmd)
    # pyautogui.click(x=pos_glasses[dst][0], y=pos_glasses[dst][1])

def bot(move_description, pos_glasses):
    glasses_blocked_until = {}
    for pos in pos_glasses:
        glasses_blocked_until[pos] = time.time()


    while len(move_description) > 0:
        if glasses_blocked_until[pos_glasses[move_description[0][0]]] < time.time() and glasses_blocked_until[pos_glasses[move_description[0][1]]] < time.time() :
            anz = move_description[0][2]
            glasses_blocked_until[pos_glasses[move_description[0][0]]] = time.time() + 1.2 + 0.7 * anz
            do_move(move_description.pop(0), pos_glasses)
        # time.sleep(0.1)
    print("Solved")

def find_image(path):
    os.environ['PATH'] = 'C:/Program Files/platform-tools/'

    os.system("adb exec-out screencap -p > pic.png")
    image = cv2.imread("pic.png",cv2.COLOR_RGB2GRAY)

    method = cv2.TM_CCOEFF_NORMED
    small_image = cv2.imread(path,cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(image, small_image, method)

    _,w,h = small_image.shape[::-1]
    print(w,h,_)
    threshold = 0.8

    loc = np.where ( result >= threshold)

    for pt in zip(*loc[::-1]):
        # cv2.rectangle(image, pt,(pt[0] + w, pt[1] + h), (0,255,255),2)
        # # cv2.imshow("found results",image)
        # # cv2.waitKey(0)
        return (True,pt[0] + w//2, pt[1] + h //2 )

    return (False, None, None)
    # We want the minimum squared difference
    # mn, _, mnLoc, _ = cv2.minMaxLoc(result)

    # # Draw the rectangle:
    # # Extract the coordinates of our best match
    # MPx, MPy = mnLoc

    # # Step 2: Get the size of the template. This is the same size as the match.
    # trows, tcols = small_image.shape[:2]
    # return (MPx + tcols // 2, MPy + trows // 2)

def playagain():

    found,X,Y = find_image("enjoyUsTiny.png")
    if found:
        print("cross",X,Y)
        cmd = f"adb shell input tap {X} {Y}"
        os.system(cmd)   

    else:
        found, X,Y = find_image("playbutton.png")
        cmd = f"adb shell input tap {X} {Y}"
        os.system(cmd)

    time.sleep(4)