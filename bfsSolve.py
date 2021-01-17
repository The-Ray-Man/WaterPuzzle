import numpy as np
from copy import deepcopy

from collections import deque


k = 4
n = 4
start = np.array(
    [[1, 2, 3, 2], [1, 4, 3, 5], [6, 5, 1, 1], [4, 7, 8, 9], [6, 9, 7, 4], [8, 9, 9, 3], [3, 6, 5, 4], [5, 6, 7, 8],
     [8, 2, 2, 7], [0, 0, 0, 0], [0, 0, 0, 0]])

# maps state to an id
global already_checked

# maps id to parent
global parent

# maps id to move that lead here
global howDidIGetHere


def sortNHash(state):
    sorted_state = state[np.lexsort(np.transpose(state)[::-1])]
    byte_state = sorted_state.data.tobytes()
    return byte_state


# Takes a state and yields all possible following states
def possibilities(state):
    topElements = [topElm(x) for x in state]
    pos_moves = []
    for (src, (top_color_src, same_colors_src, free_spaces_src)) in enumerate(topElements):
        for (dst, (top_color_dst, same_colors_dst, free_spaces_dst)) in enumerate(topElements):
            if (top_color_dst == top_color_src or top_color_dst == 0) and free_spaces_dst > 0 and src != dst:
                if same_colors_src <= free_spaces_dst:
                    anz = same_colors_src
                else:
                    anz = free_spaces_dst
                if same_colors_dst + anz == k:
                    return [(src, k - free_spaces_src - anz, dst, k - free_spaces_dst, anz)]
                else:
                    pos_moves.append((src, k - free_spaces_src - anz, dst, k - free_spaces_dst,
                                      anz))  # (source,pos_source,destination,pos_dest, anz)

    return pos_moves


def doMove(state, move):
    source, source_pos, destination, dest_pos, anz = move
    for i, p in enumerate(range(source_pos, source_pos + anz)):
        state[destination][dest_pos + i] = state[source][p]
        state[source][p] = 0
    # print("in do move \n",state)
    return state


def topElm(glass):
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
        counter = k
    return top_color, counter, free_spaces  # (upper color, anz same colors, free space)


def solved(state):
    return all(all(glass[0] == fluid for fluid in glass[1:]) for glass in state)


def solve(glasses):

    global already_checked
    already_checked = dict()

    global parent
    parent = dict()

    global howDidIGetHere
    howDidIGetHere = dict()

    q = deque()
    q.append(glasses)
    parent[0] = -1
    already_checked[sortNHash(glasses)] = 0

    # i know this ugly
    solvedId = -2

    idCounter = 1
    while q:
        currState = q.popleft()

        currId = already_checked[sortNHash(currState)]
        # todo check before adding to queue
        # exit condition

        if solved(currState):
            solvedId = currId
            print("solved", currId)

            # todo: reverse the voyage
            break

        for pos in possibilities(currState):
            # creates a new hypothetical state based on teh current state and a possible move
            hypState = doMove(deepcopy(currState), pos)

            if sortNHash(hypState) in already_checked:
                continue
            already_checked[sortNHash(hypState)] = idCounter
            parent[idCounter] = currId
            howDidIGetHere[idCounter] = pos

            idCounter += 1
            q.append(hypState)

    print(solvedId)
    if solvedId == -2:
        print("no solution found")
        return False, []

    currPar = solvedId
    path = []
    while currPar != 0:
        path.append(howDidIGetHere[currPar])
        currPar = parent[currPar]

    path.reverse()
    solution = []
    for p in path:
        solution.append((p[0], p[2], p[4]))
    return True, solution
