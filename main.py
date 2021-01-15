import numpy as np
from copy import deepcopy

k = 4
n = 4
start = np.array(
    [[1, 2, 3, 2], [1, 4, 3, 5], [6, 5, 1, 1], [4, 7, 8, 9], [6, 9, 7, 4], [8, 9, 9, 3], [3, 6, 5, 4], [5, 6, 7, 8],
     [8, 2, 2, 7], [0, 0, 0, 0], [0, 0, 0, 0]])

already_checked = dict()


def sort(state):
    sorted_state = state[np.lexsort(np.transpose(state)[::-1])]
    byte_state = sorted_state.data.tobytes()
    return byte_state


def decant(state, pass_solution, max_depth):
    if solved(state):
        # print("found Solution")
        # solution.append(state)
        return True, pass_solution

    if sort(state) in already_checked:
        if already_checked[sort(state)] <= len(pass_solution):
            return False, []
    already_checked[sort(state)] = len(pass_solution)

    if len(pass_solution) >= max_depth:
        # print("max depth")
        return False, []

    solution = None

    for pos in possibilities(state):
        if pass_solution and pass_solution[-1] == (pos[2], pos[0]):
            continue
        # print(pos)
        new_state = doMove(deepcopy(state), pos)
        # print(new_state)

        found_solution, possible_solution = decant(new_state, pass_solution + [(pos[0], pos[2])], max_depth)
        if found_solution:
            # print(len(possible_solution))
            if len(possible_solution) < max_depth:
                # print("new good solution", possible_solution)
                solution = possible_solution
                max_depth = len(possible_solution)
    if solution:
        return True, solution
    return False, []


def doMove(state, move):
    source, source_pos, destination, dest_pos, anz = move
    for i, p in enumerate(range(source_pos, source_pos + anz)):
        state[destination][dest_pos + i] = state[source][p]
        state[source][p] = 0
    # print("in do move \n",state)
    return state


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
                    # print("good move")
                    return [(src, k - free_spaces_src - anz, dst, k - free_spaces_dst, anz)]
                else:
                    pos_moves.append((src, k - free_spaces_src - anz, dst, k - free_spaces_dst,
                                      anz))  # (source,pos_source,destination,pos_dest, anz)

    return pos_moves


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

found_solution_, solution_ = decant(start, [], 200)
if found_solution_:
    print(solution_, len(solution_))
else:
    print("maybe impossible to solve!")
