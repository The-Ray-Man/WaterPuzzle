from bfsSolve import *
from visuals import *
from bot import *
import numpy as np

while True:
    glasses, glasses_pos = read_display()
    # print(glasses)
    print(np.asarray(glasses))
    if glasses:
        found_solution_, solution_ = solve(np.asarray(glasses))
        if found_solution_:
            print("Solution: ", solution_)
            bot(solution_, glasses_pos)
            if not playagain():
                playagain()
