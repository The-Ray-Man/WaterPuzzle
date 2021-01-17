from bfsSolve import *
from visuals import *
from bot import *
import numpy as np
from ppadb.client import Client as AdbClient

MOVE_DELAY = 0.9
FILL_DELAY = 0.6

SLOW_MOVE_DELAY = 1.5
SLOW_FILL_DELAY = 1

client = AdbClient(host="127.0.0.1", port=5037)
device = client.devices()[0]

bfs = BfsSolve(4, False)
bot = Bot(device, MOVE_DELAY, FILL_DELAY, SLOW_MOVE_DELAY, SLOW_FILL_DELAY, False)


failed_solves = 0


def solve(mode):
    glasses, glasses_pos = read_display(device)
    if not glasses:
        print("No glasses found")
        return False
    print(np.asarray(glasses))
    found_solution, solution = bfs.solve(np.asarray(glasses))
    if not found_solution:
        bot.press_replay()
        return False
    bot.solve(solution, glasses_pos, mode)
    return True

solve_mode = 0

while True:
    if solve_mode <= 1:
        if solve(0):
            if not bot.play_again():
                time.sleep(2.5)
                solve_mode += 1
            else:
                # everything successful
                solve_mode = 0
                time.sleep(2.5)
        else:
            bot.play_again()
    else:
        time.sleep(3)
        bot.press_replay()
        if solve(1):
            if not bot.play_again():
                time.sleep(2.5)
                solve_mode += 1
            else:
                # everything successful
                solve_mode = 0
                time.sleep(2.5)
        else:
            bot.play_again()
            time.sleep(3)



    # glasses, glasses_pos = read_display(device)
    # # print(glasses)
    # print(np.asarray(glasses))
    # if glasses:
    #     found_solution, solution = bfs.solve(np.asarray(glasses))
    #     if found_solution:
    #         print("Solution: ", solution)
    #         bot.solve(solution, glasses_pos)
    #         if not bot.play_again():
    #             failed_solves += 1
    #             if failed_solves > 1:
    #                 glasses, glasses_pos = read_display(device)
    #                 found_solution, solution = bfs.solve(np.asarray(glasses))
    # else:
    #     bot.play_again()



