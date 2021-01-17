import time
import cv2
import numpy as np
import os
import platform

if platform.system() == "Windows":
    os.environ['PATH'] = 'C:/Program Files/platform-tools/'

MOVE_DELAY = 1.1
FILL_DELAY = 0.7


def do_move(move_description, pos_glasses):
    src, dst, anz = move_description
    cmd = f"adb shell input tap {pos_glasses[src][0]} {pos_glasses[src][1]}"
    os.system(cmd)
    # pyautogui.click(x=pos_glasses[src][0], y=pos_glasses[src][1])
    time.sleep(0.2)

    cmd = f"adb shell input tap {pos_glasses[dst][0]} {pos_glasses[dst][1]}"
    os.system(cmd)
    # pyautogui.click(x=pos_glasses[dst][0], y=pos_glasses[dst][1])


def optimize_moves(move_description):
    blacklist = set()
    sorted_moves = []
    parallel_moves = []
    
    while len(move_description) > 0:
        remove_moves = []
        for i, mov in enumerate(move_description):
            src, dst, anz = mov
            canDo = True
            if src in blacklist:
                canDo = False
            if dst in blacklist:
                canDo = False

            blacklist.add(src)
            blacklist.add(dst)

            if canDo:
                remove_moves.append(i)
                parallel_moves.append(mov)
                # print("b",blacklist)
        blacklist = set()
        sorted_moves.append(parallel_moves)
        n_move_description = []
        for i in range(len(move_description)):
            if not i in remove_moves:
                n_move_description.append(move_description[i])
            # move_description.remove()
        move_description = n_move_description
        parallel_moves = []
    
    return sorted_moves


def move_possible(glasses_blocked_until,pos_glasses,src_glass, dst_glass):
    return (glasses_blocked_until[pos_glasses[src_glass]] < time.time() and glasses_blocked_until[pos_glasses[dst_glass]] < time.time())



def bot(move_description, pos_glasses):
    glasses_blocked_until = {}

    sorted_moves = optimize_moves(move_description)
    print("sorted moves:", sorted_moves)
    for pos in pos_glasses:
        glasses_blocked_until[pos] = time.time()
        # print(glasses_blocked_until[pos], ids_)

    last_move_length = 4
    blacklist = []
    for i in range(len(sorted_moves)):
        while len(sorted_moves[i]) > 0:
            for src_glass, dst_glass, anz in sorted_moves[i]:
                if move_possible(glasses_blocked_until,pos_glasses,src_glass,dst_glass):
                    # anz = move_description[0][2]
                    glasses_blocked_until[pos_glasses[src_glass]] = time.time() + MOVE_DELAY + FILL_DELAY * anz
                    last_move_length = anz
                    do_move((src_glass,dst_glass,anz), pos_glasses)
                    sorted_moves[i].remove((src_glass,dst_glass,anz))

            blacklist = []
        # time.sleep(0.1)
    time.sleep(MOVE_DELAY + FILL_DELAY * last_move_length - 0.5)
    print("Solved")


def find_image(path):
    if platform.system() == "Windows":
        os.environ['PATH'] = 'C:/Program Files/platform-tools/'
        os.system("adb exec-out screencap -p > pic.png")
    else:
        os.system("adb shell screencap -p > pic.png")
    image = cv2.imread("pic.png", cv2.COLOR_RGB2GRAY)

    method = cv2.TM_CCOEFF_NORMED
    small_image = cv2.imread(path, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(image, small_image, method)

    _, w, h = small_image.shape[::-1]
    print(w, h, _)
    threshold = 0.8

    loc = np.where(result >= threshold)

    for pt in zip(*loc[::-1]):
        # cv2.rectangle(image, pt,(pt[0] + w, pt[1] + h), (0,255,255),2)
        # # cv2.imshow("found results",image)
        # # cv2.waitKey(0)
        return (True, pt[0] + w // 2, pt[1] + h // 2)

    return (False, None, None)
    # We want the minimum squared difference
    # mn, _, mnLoc, _ = cv2.minMaxLoc(result)

    # # Draw the rectangle:
    # # Extract the coordinates of our best match
    # MPx, MPy = mnLoc


def playagain():
    found, X, Y = find_image("enjoyUsTiny.png")
    if not found:
        found, X, Y = find_image("playbutton.png")
        if not found:
            found, X, Y = find_image("replaybutton.png")
            if not found:
                print("Play button and cross not found, error while solving likely")
                time.sleep(2)
                return False

    cmd = f"adb shell input tap {X} {Y}"
    os.system(cmd)


    time.sleep(2)
    return True


