from bfsSolve import *
from visuals import *
from bot import *
import numpy as np
from ppadb.client import Client as AdbClient

client = AdbClient(host="127.0.0.1", port=5037)

device = client.devices()[0]

while True:
    glasses, glasses_pos = read_display(device)
    # print(glasses)
    print(np.asarray(glasses))
    if glasses:
        found_solution_, solution_ = solve(np.asarray(glasses))
        if found_solution_:
            print("Solution: ", solution_)
            bot(solution_, glasses_pos, device)
            if not playagain(device):
                playagain(device)
    else:
        playagain(device)