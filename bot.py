import pyautogui
import time

def do_move(move_description, pos_glasses):
    src, dst = move_description

    pyautogui.moveTo(pos_glasses[src])
    pyautogui.click(x=pos_glasses[src][0], y=pos_glasses[src][1])
    pyautogui.click(x=pos_glasses[dst][0], y=pos_glasses[dst][1])
    time.sleep(2)


def bot(move_description,pos_glasses):
    for move in move_description:
        do_move(move,pos_glasses)
    print("Solved")