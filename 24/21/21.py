from collections import deque

#
# 1) Define the layouts of each keypad as grids of valid positions.
#
#    For simplicity, we’ll store them as a dict:
#       keypad_name -> {
#         "grid": {(x, y): char, ...},   # which character is at each coordinate
#         "start": (start_x, start_y),   # coordinate of 'A' (the pointer start)
#         "width": w, "height": h
#       }
#    The numeric keypad has the layout:
#        7(0,0)  8(1,0)  9(2,0)
#        4(0,1)  5(1,1)  6(2,1)
#        1(0,2)  2(1,2)  3(2,2)
#        (gap)   0(1,3)  A(2,3)
#
#    Each directional keypad has the layout:
#         ^(1,0), A(2,0)
#    <(0,1), v(1,1), >(2,1)
#

def build_numeric_keypad():
    """
    Build a representation of the numeric keypad:
        +---+---+---+
        | 7 | 8 | 9 |
        +---+---+---+
        | 4 | 5 | 6 |
        +---+---+---+
        | 1 | 2 | 3 |
        +---+---+---+
            | 0 | A |
            +---+---+
    """
    grid = {}
    # row 0
    grid[(0,0)] = '7'
    grid[(1,0)] = '8'
    grid[(2,0)] = '9'
    # row 1
    grid[(0,1)] = '4'
    grid[(1,1)] = '5'
    grid[(2,1)] = '6'
    # row 2
    grid[(0,2)] = '1'
    grid[(1,2)] = '2'
    grid[(2,2)] = '3'
    # row 3
    # (0,3) is gap, do not include
    grid[(1,3)] = '0'
    grid[(2,3)] = 'A'  # this is the pointer start
    return {
        "grid": grid,
        "start": (2,3),  # 'A'
        "width": 3,
        "height": 4
    }

def build_directional_keypad():
    """
    Build a representation of a directional keypad:
         +---+---+
         | ^ | A |
      +---+---+---+
      | < | v | > |
      +---+---+---+
    Coordinates (x,y):
         ^(1,0), A(2,0)
    <(0,1), v(1,1), >(2,1)
    We'll assume 'A' is at (1,0) *or* (2,0). The puzzle text says:
       "When the robot arrives... its robotic arm is pointed at the A button in the bottom right corner"
    But for the second robot it's "upper right corner." 
    The puzzle's exact placement can vary; we'll pick a consistent layout that matches the text for the BFS.
    """
    grid = {}
    # top row
    grid[(1,0)] = '^'
    grid[(2,0)] = 'A'
    # bottom row
    grid[(0,1)] = '<'
    grid[(1,1)] = 'v'
    grid[(2,1)] = '>'
    # Let’s say the start is always at (2,0) for the robot that starts pointed at A (upper right).
    return {
        "grid": grid,
        "start": (2,0),  # 'A'
        "width": 3,
        "height": 2
    }

#
# 2) BFS on a single keypad to type a desired string (e.g. "029A"), returning the minimal sequence
#    of '^', 'v', '<', '>', 'A'.
#
#    - We start with pointer at keypad["start"].
#    - We want to produce exactly `target_string` in order (the next press of 'A' must match
#      target_string[next_index], or else that path is invalid).
#    - We never move pointer into a coordinate that doesn't exist in the grid.
#    - Pressing 'A' increments next_index only if the current pointer's character matches the
#      needed character in `target_string`.
#

def bfs_type_string(keypad, target_string):
    """
    Returns the *shortest* sequence of '^', 'v', '<', '>', 'A'
    needed on this keypad to type `target_string`.
    If impossible, returns None.
    """
    grid = keypad["grid"]
    start_pos = keypad["start"]
    
    # BFS queue: each entry is (pos, idx, path_so_far)
    #   pos = (x,y) pointer location
    #   idx = how many characters of target_string are typed so far
    #   path_so_far = string of button presses leading here
    queue = deque()
    queue.append((start_pos, 0, ""))

    # visited set to avoid revisiting the same (pos, idx)
    visited = set()
    visited.add((start_pos, 0))

    # Offsets for movement
    moves = {
        '^': (0, -1),
        'v': (0,  1),
        '<': (-1, 0),
        '>': (1,  0)
    }

    while queue:
        pos, idx, path = queue.popleft()
        if idx == len(target_string):
            # We have typed the full target
            return path

        # For each movement button: ^, v, <, >
        for move_button, (dx, dy) in moves.items():
            new_x = pos[0] + dx
            new_y = pos[1] + dy
            new_pos = (new_x, new_y)
            # If valid position (in grid):
            if new_pos in grid:
                if (new_pos, idx) not in visited:
                    visited.add((new_pos, idx))
                    queue.append((new_pos, idx, path + move_button))

        # For the 'A' (activate) button:
        # we only press 'A' if the character under the pointer matches target_string[idx].
        current_char = grid[pos]
        needed_char  = target_string[idx]
        if current_char == needed_char:
            # Pressing A types that character
            new_idx = idx + 1
            if (pos, new_idx) not in visited:
                visited.add((pos, new_idx))
                queue.append((pos, new_idx, path + 'A'))

    # If we exhaust BFS without success, no valid sequence
    return None


#
# 3) Nested BFS logic. 
#    Once we get a minimal sequence (like "v<<A>>^A...") for one keypad,
#    we have to produce that *exact sequence of characters* on the next-higher-level keypad.
#
#    That is, if we needed to press `'^'` on keypad #4, then we must BFS on keypad #3 to produce
#    the literal character `'^'`.  Then BFS that result on keypad #2 to produce the literal
#    string from #3, etc.
#

def nest_sequence(outer_keypad, sequence_to_produce):
    """
    Given that we want to produce the *literal* string `sequence_to_produce`
    (each character is '^', 'v', '<', '>', or 'A')
    on `outer_keypad`, return the minimal BFS string of '^', 'v', '<', '>', 'A'
    that yields exactly `sequence_to_produce`.
    """
    # We treat each character in sequence_to_produce as the “target string” in BFS.
    # But we have to type them in order, so the BFS “target string” is literally the sequence itself.
    return bfs_type_string(outer_keypad, sequence_to_produce)


#
# 4) Putting it all together to type a code on the numeric keypad
#    from the user’s “outermost” keypad.  In the puzzle text:
#      - The numeric keypad is typed by Robot 1.
#      - Robot 1’s keypad is typed by Robot 2.
#      - Robot 2’s keypad is typed by you (the puzzle says “two directional keypads that robots
#        are using, and one directional keypad that you are using”).
#
#    For demonstration, we'll assume a chain:
#       YOU (#1) -> Robot2Keypad (#2) -> Robot1Keypad (#3) -> NumericKeypad (#4)
#    In practice, you just adapt the code if your chain differs.
#

def get_final_sequence_for_code(code, keypad_you, keypad_robot2, keypad_robot1, keypad_numeric):
    """
    1) BFS on the numeric keypad (#4) to type `code`, yielding seq4.
    2) BFS on robot1 keypad (#3) to produce the *literal* characters of seq4, yielding seq3.
    3) BFS on robot2 keypad (#2) to produce the *literal* characters of seq3, yielding seq2.
    4) BFS on your keypad (#1)   to produce the *literal* characters of seq2, yielding seq1.
    Return seq1, the final sequence you press.
    """
    # Step 1: minimal sequence on numeric keypad
    seq4 = bfs_type_string(keypad_numeric, code)
    if seq4 is None:
        raise ValueError(f"Cannot type {code} on the numeric keypad!")
    # Step 2: minimal sequence on robot1 keypad
    seq3 = nest_sequence(keypad_robot1, seq4)
    if seq3 is None:
        raise ValueError(f"Cannot produce seq4 on robot1 keypad!")
    # Step 3: minimal sequence on robot2 keypad
    seq2 = nest_sequence(keypad_robot2, seq3)
    if seq2 is None:
        raise ValueError(f"Cannot produce seq3 on robot2 keypad!")
    # Step 4: minimal sequence on *your* keypad
    seq1 = nest_sequence(keypad_you, seq2)
    if seq1 is None:
        raise ValueError(f"Cannot produce seq2 on your keypad!")
    return seq1


#
# 5) Complexity:
#      complexity(code) = (length of seq1) * (integer value of code ignoring leading zeros).
#

def code_complexity(code, seq1):
    """
    Return complexity = (length of seq1) * (numeric_value_of_code).
    code e.g. '029A' -> numeric part is 29.
    """
    # Strip trailing 'A' if necessary, because codes might always end with 'A'. 
    # But puzzle says “The numeric part of the code (ignoring leading zeroes)” – 
    # the letter 'A' is not in that numeric part anyway.
    # Example: "029A" -> numeric part "029" -> integer is 29.
    # Another example: "456A" -> numeric part "456" -> integer is 456.
    # We'll just remove all non-digit characters and parse.
    numeric_part = "".join(ch for ch in code if ch.isdigit())
    if numeric_part == "":
        numeric_val = 0
    else:
        numeric_val = int(numeric_part)  # leading zeroes become ignored
    return len(seq1) * numeric_val


#
# 6) Putting it all together to solve a list of codes.
#

def solve_codes(codes):
    # Build all 4 keypads (the chain):
    keypad_you = build_directional_keypad()    # your keypad
    keypad_robot2 = build_directional_keypad() # robot #2’s keypad
    keypad_robot1 = build_directional_keypad() # robot #1’s keypad
    keypad_numeric = build_numeric_keypad()    # final numeric keypad

    total = 0
    for code in codes:
        # Ensure code ends with 'A' if that’s required by puzzle. The puzzle often has codes like "029A".
        # We'll assume the input includes that trailing 'A', but adapt as needed.
        seq1 = get_final_sequence_for_code(
            code,
            keypad_you,
            keypad_robot2,
            keypad_robot1,
            keypad_numeric
        )
        total += code_complexity(code, seq1)
    return total


#
# 7) Example usage:
#

if __name__ == "__main__":
    example_codes = ["029A", "980A", "179A", "456A", "379A"]
    answer = solve_codes(example_codes)
    print("Sum of complexities =", answer)
