import time
import cv2
import numpy as np


class Bot:
    def __init__(self, device, move_delay, fill_delay, slow_move_delay, slow_fill_delay, debug):
        self.device = device
        self.move_delay = move_delay
        self.fill_delay = fill_delay

        self.slow_move_delay = slow_move_delay
        self.slow_fill_delay = slow_fill_delay

        self.debug = debug

    def do_move(self, move_description, pos_glasses):
        src, dst, anz = move_description
        cmd = f"input tap {pos_glasses[src][0]} {pos_glasses[src][1]}"
        self.device.shell(cmd)
        # pyautogui.click(x=pos_glasses[src][0], y=pos_glasses[src][1])

        time.sleep(0.1)

        cmd = f"input tap {pos_glasses[dst][0]} {pos_glasses[dst][1]}"
        self.device.shell(cmd)
        # pyautogui.click(x=pos_glasses[dst][0], y=pos_glasses[dst][1])

    @staticmethod
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

    @staticmethod
    def move_possible(glasses_blocked_until, pos_glasses, src_glass, dst_glass):
        return (glasses_blocked_until[pos_glasses[src_glass]] < time.time() and glasses_blocked_until[
            pos_glasses[dst_glass]] < time.time())

    def solve(self, move_description, pos_glasses, mode):
        if mode == 1:
            for scr, dst, anz in move_description:
                self.do_move((scr, dst, anz), pos_glasses)
                time.sleep(self.slow_move_delay + self.slow_fill_delay * anz)
        else:
            glasses_blocked_until = {}
            sorted_moves = self.optimize_moves(move_description)

            print("sorted moves:", sorted_moves)
            for pos in pos_glasses:
                glasses_blocked_until[pos] = time.time()
                # print(glasses_blocked_until[pos], ids_)

            last_move_length = 4
            for i in range(len(sorted_moves)):
                while len(sorted_moves[i]) > 0:
                    for src_glass, dst_glass, anz in sorted_moves[i]:
                        if self.move_possible(glasses_blocked_until, pos_glasses, src_glass, dst_glass):
                            # anz = move_description[0][2]
                            last_move_length = anz
                            self.do_move((src_glass, dst_glass, anz), pos_glasses)
                            glasses_blocked_until[pos_glasses[src_glass]] = time.time() + \
                                self.move_delay + self.fill_delay * anz
                            sorted_moves[i].remove((src_glass, dst_glass, anz))

                # time.sleep(0.1)
            time.sleep(self.move_delay + self.fill_delay * last_move_length)
        print("Solved")

    def find_image(self, path):

        result = self.device.screencap()
        with open("pic.png", "wb") as fp:
            fp.write(result)
        image = cv2.imread("pic.png", cv2.COLOR_RGB2GRAY)

        method = cv2.TM_CCOEFF_NORMED
        small_image = cv2.imread(path, cv2.COLOR_RGB2GRAY)

        result = cv2.matchTemplate(image, small_image, method)

        _, w, h = small_image.shape[::-1]
        print(w, h, _)
        threshold = 0.6

        loc = np.where(result >= threshold)

        for pt in zip(*loc[::-1]):
            # cv2.rectangle(image, pt,(pt[0] + w, pt[1] + h), (0,255,255),2)
            # # cv2.imshow("found results",image)
            # # cv2.waitKey(0)
            return True, pt[0] + w // 2, pt[1] + h // 2

        return False, None, None
        # We want the minimum squared difference
        # mn, _, mnLoc, _ = cv2.minMaxLoc(result)

        # # Draw the rectangle:
        # # Extract the coordinates of our best match
        # MPx, MPy = mnLoc

    def play_again(self):
        found, X, Y = self.find_image("playbutton.png")
        if not found:
            found, X, Y = self.find_image("enjoyUsTiny.png")
            if not found:
                print("Play button and cross not found, error while solving likely")
                return False

        cmd = f"input tap {X} {Y}"
        self.device.shell(cmd)

        return True

    def press_replay(self):
        found, X, Y = self.find_image("replaybutton.png")
        if found:
            cmd = f"input tap {X} {Y}"
            self.device.shell(cmd)
        else:
            print("Replay not found")
