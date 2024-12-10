import sys; args = sys.argv[1:]
import time


def set_globals(pzl):
    global LOCS, POS_TO_LOCS, NEIGHBORS, SYMBOL_SET, STATS, SYMBOL_SET_LENGTH, PL, SL
    PL = len(pzl)
    SL = int(len(pzl) ** 0.5)  # side length
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    NUMBERS = "123456789"
    SYMBOLS_IN_PZL = {*pzl} - {"."}
    if SL == len(SYMBOLS_IN_PZL): SYMBOL_SET = SYMBOLS_IN_PZL
    else:
        for n in NUMBERS:
            if SL == len(SYMBOLS_IN_PZL): break
            else: SYMBOLS_IN_PZL.add(n)
        else:  # use letters, out of numbers, only runs if still not enough characters
            for char in ALPHABET:
                if SL == len(SYMBOLS_IN_PZL): break
                else: SYMBOLS_IN_PZL.add(char)
    SYMBOL_SET_LENGTH = len(SYMBOL_SET)
    LOCS = [{i for i in range(n, n + SL)} for n in range(0, PL, SL)] +\
           [{i for i in range(n, PL, SL)} for n in range(0, SL)]  # rows, columns
    cubeLengths = {  # pzl size: horizontal length, vertical length
        4*4: (2, 2),
        6*6: (3, 2),
        8*8: (4, 2),
        9*9: (3, 3),
        12*12: (4, 3),
        16*16: (4, 4)
    }
    horizontal_length, vertical_length = cubeLengths[PL]
    for left_cube_index in range(0, PL, horizontal_length):
        row_idx = left_cube_index // SL  # zero indexed
        if row_idx % vertical_length != 0: continue
        cube = {row_mul*SL+column
                for column in range(left_cube_index, left_cube_index+horizontal_length)
                for row_mul in range(0, vertical_length)}
        LOCS.append(cube)
    POS_TO_LOCS = {n: [CS for CS in LOCS if n in CS] for n in range(len(pzl))}
    NEIGHBORS = {idx: {elem for cs in POS_TO_LOCS[idx] for elem in cs if elem != idx}for idx in POS_TO_LOCS}
    try:  # check if it exists, don't redeclare for each run
        e = len(STATS) > 0
    except Exception as e:
        STATS = {}


def updateStats(s: str):
    if s in STATS: STATS[s] += 1
    else: STATS[s] = 1


def place(pzl, idx, number):
    updateStats("PLACE RETURN")
    return f"{pzl[:idx]}{str(number)}{pzl[idx + 1:]}"


def is_invalid(pzl, idx, elem=None):  # can pass pzl and idx, if pass elem you dont need to send modified pzl
    if idx is None:  # if None, always root, it is always solvable
        return False
    for neighbor_idx in NEIGHBORS[idx]:  # loop through set of indices of constraint sets
        if idx == neighbor_idx: continue
        if (pzl[idx] if elem is None else elem) == pzl[neighbor_idx]:
            return True
    updateStats("INVALID RETURN")
    return False


def findOptimalDot(pzl, c_dict) -> tuple:  # length of possible values , index of optimal dot
    min_length = SYMBOL_SET_LENGTH + 1
    min_idx = 0
    for idx in range(len(pzl)):
        if pzl[idx] == ".":
            if len(c_dict[idx]) == 0:
                return -1, -1  # invalid
            elif len(c_dict[idx]) == 1:
                return 1, idx
            elif len(c_dict[idx]) < min_length:
                min_idx = idx
                min_length = len(c_dict[idx])
    updateStats("OPTIMAL DOT RETURN")
    return min_length, min_idx


def findOptimalSymbol(pzl, c_dict):
    optimal_length = SYMBOL_SET_LENGTH + 1
    global_best_min = None, []
    for CS in LOCS:
        chars_in_cs = {pzl[idx] for idx in CS} - {"."}
        chars_not_found = SYMBOL_SET - chars_in_cs
        for char in chars_not_found:
            valid_positions = [idx for idx in CS
                               if char in c_dict[idx] and pzl[idx] == "."]  # if
            number_of_valid_positions = len(valid_positions)
            if number_of_valid_positions == 1:
                return char, valid_positions
            elif number_of_valid_positions < optimal_length:
                global_best_min = (char,  valid_positions)
                optimal_length = number_of_valid_positions
    return global_best_min


def brute_force(pzl, c_dict):
    if "." not in pzl: return pzl
    dot_pos_length, dot_pos = findOptimalDot(pzl, c_dict)  # get optimal dot index
    if dot_pos_length == -1: return ""  # if no solution, return
    if dot_pos_length != 1:  # if more than one solution
        char, symbol_pos_list = findOptimalSymbol(pzl, c_dict)  # optimal character index list
        if 0 < len(symbol_pos_list) < dot_pos_length:  # if optimal symbol is better
            children = [(pos, place(pzl, pos, char)) for pos in symbol_pos_list]
        else:
            children = [(dot_pos, place(pzl, dot_pos, s)) for s in c_dict[dot_pos]]
    else:  # if only one solution, don't have to run optimal symbol
        children = [(dot_pos, place(pzl, dot_pos, *c_dict[dot_pos]))]
    for i, subPzlTuple in enumerate(children):
        pos, subPzl = subPzlTuple
        if i == len(children) - 1: c_new = c_dict  # if last iteration in children
        else: c_new = {key: {*c_dict[key]} for key in c_dict}  # else copy it
        for idx in NEIGHBORS[pos]:
            c_new[idx] -= {subPzl[pos]}
        bF = brute_force(subPzl, c_new)
        if bF: return bF
    return ""


def check_sum(pzl):
    return sum(ord(str(e)) - ord("1") for e in pzl)  # return sum of ascii values - min values


def rect_print(pzl):
    print("\n".join(
        [" ".join([s for s in pzl[i:i + int(len(pzl) ** 0.5)]]) for i in range(0, len(pzl), int(len(pzl) ** 0.5))]))
    print()

def main():
    file_path = "puzzles.txt"
    with open(file_path) as f:
        s = [line.strip() for line in f]
    run_start = time.process_time()

    for i, pzl in enumerate(s):
        pzl_start = time.process_time()
        set_globals(pzl)
        cd = {
            idx: {s for s in SYMBOL_SET if not is_invalid(pzl, idx, elem=s)}
            if pzl[idx] == "." else set()
            for idx in range(len(pzl))}
        solution = brute_force(pzl, cd)

        print(f"{i + 1}: {pzl}")
        spaces = " " * (len(str(i + 1)) + 2)
        print(f"{spaces}{solution} {check_sum(solution)} {(time.process_time() - pzl_start):.4f}")

    print(STATS)
    run_end = time.process_time()
    print(f"Total Time: {run_end-run_start:.4f}")


if __name__ == '__main__': main()