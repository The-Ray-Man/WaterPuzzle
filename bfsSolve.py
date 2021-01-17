import numpy as np
from copy import deepcopy

from collections import deque


class BfsSolve:
    def __init__(self, k, debug):
        # maps state to an id
        self.already_checked = dict()
        # maps id to parent
        self.parent = dict()
        # maps id to move that lead here
        self.howDidIGetHere = dict()

        self.k = k

        self.debug = debug

    @staticmethod
    def sortNHash(state):
        sorted_state = state[np.lexsort(np.transpose(state)[::-1])]
        byte_state = sorted_state.data.tobytes()
        return byte_state

    # Takes a state and yields all possible following states
    def possibilities(self, state):
        topElements = [self.topElm(x) for x in state]
        pos_moves = []
        for (src, (top_color_src, same_colors_src, free_spaces_src)) in enumerate(topElements):
            for (dst, (top_color_dst, same_colors_dst, free_spaces_dst)) in enumerate(topElements):
                if (top_color_dst == top_color_src or top_color_dst == 0) and free_spaces_dst > 0 and src != dst:
                    if same_colors_src <= free_spaces_dst:
                        anz = same_colors_src
                    else:
                        anz = free_spaces_dst
                    if same_colors_dst + anz == self.k:
                        return [(src, self.k - free_spaces_src - anz, dst, self.k - free_spaces_dst, anz)]
                    else:
                        pos_moves.append((src, self.k - free_spaces_src - anz, dst, self.k - free_spaces_dst,
                                          anz))  # (source,pos_source,destination,pos_dest, anz)

        return pos_moves

    @staticmethod
    def doMove(state, move):
        source, source_pos, destination, dest_pos, anz = move
        for i, p in enumerate(range(source_pos, source_pos + anz)):
            state[destination][dest_pos + i] = state[source][p]
            state[source][p] = 0
        # print("in do move \n",state)
        return state

    def topElm(self, glass):
        x = 1
        free_spaces = 0
        while glass[-x] == 0:
            free_spaces += 1
            if x >= len(glass):
                break
            x += 1
        top_color = glass[-x]
        counter = 0
        if top_color != 0:
            while top_color == glass[-x]:
                counter += 1
                if x >= len(glass):
                    break
                x += 1
        else:
            counter = self.k
        return top_color, counter, free_spaces  # (upper color, anz same colors, free space)

    @staticmethod
    def solved(state):
        return all(all(glass[0] == fluid for fluid in glass[1:]) for glass in state)

    def solve(self, glasses):

        self.already_checked = dict()
        self.parent = dict()
        self.howDidIGetHere = dict()

        q = deque()
        q.append(glasses)
        self.parent[0] = -1
        self.already_checked[self.sortNHash(glasses)] = 0

        # i know this ugly
        solvedId = -2

        idCounter = 1
        while q:
            currState = q.popleft()

            currId = self.already_checked[self.sortNHash(currState)]
            # todo check before adding to queue
            # exit condition

            if self.solved(currState):
                solvedId = currId
                print("solved! tested states: ", currId)

                # todo: reverse the voyage
                break

            for pos in self.possibilities(currState):
                # creates a new hypothetical state based on teh current state and a possible move
                hypState = self.doMove(deepcopy(currState), pos)

                if self.sortNHash(hypState) in self.already_checked:
                    continue
                self.already_checked[self.sortNHash(hypState)] = idCounter
                self.parent[idCounter] = currId
                self.howDidIGetHere[idCounter] = pos

                idCounter += 1
                q.append(hypState)

        # print(solvedId)
        if solvedId == -2:
            print("no solution found")
            return False, []

        currPar = solvedId
        path = []
        while currPar != 0:
            path.append(self.howDidIGetHere[currPar])
            currPar = self.parent[currPar]

        path.reverse()
        solution = []
        for p in path:
            solution.append((p[0], p[2], p[4]))
        blocked_glasses = set()
        print("solution: ", solution)
        for i in range(len(solution) - 1, -1, -1):
            if solution[i][0] not in blocked_glasses and solution[i][1] not in blocked_glasses:
                if solution[i][2] == 3:
                    solution[i] = (solution[i][1], solution[i][0], 1)
            blocked_glasses.add(solution[i][0])
            blocked_glasses.add(solution[i][1])

        return True, solution
