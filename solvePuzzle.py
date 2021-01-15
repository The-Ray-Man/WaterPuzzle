from main import *
from visuals import *
from bot import *
import numpy as np

while True:
    glasses, glasses_pos = read_display()
    print(glasses)
    print(np.asarray(glasses))
    found_solution_, solution_ = decant(np.asarray(glasses), [], 200)
    if found_solution_:
        bot(solution_,glasses_pos)
    else:
        print("maybe impossible to solve!")
        break   
    time.sleep(3)
    playagain() 