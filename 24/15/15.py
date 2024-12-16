import sys

sys.path.append("..")
from time import sleep

import numpy as np
from IPython.display import clear_output
from utils.utils import Matrix, Vec

with open("test.txt") as file:
    field, instructions = file.read().split("\n\n")
field = field.replace("#", "##")
field = field.replace("O", "[]")
field = field.replace(".", "..")
field = field.replace("@", "@.")
field = Matrix.from_str(field)
instructions = instructions.replace("\n", "")

instr_map = {
    ">" : Vec(1, 0),
    "v" : Vec(0, 1),
    "<" : Vec(-1, 0),
    "^" : Vec(0, -1)
}

shape = Vec(*field.shape)
rob = Vec(*list(zip(*np.where(field == '@')))[0])
boxes = [Vec(*box) for box in list(zip(*np.where(field == '[')))]
walls = [Vec(*box) for box in list(zip(*np.where(field == '#')))]
def print_field2(rob, boxes, walls, shape, symbol='@'):
    m = Matrix(np.full((shape.x, shape.y), '.'))
    # m = np.pad(m, ((2, 2), (1, 1)), 'constant', constant_values='#').view(Matrix)
    for wall in walls:
        m[wall] = '#'
    for box in boxes:
        m[box] = '['
        m[box + Vec(1,0)] = ']'
    m[rob] = symbol
    return str(m)
# pivot boxes on left edge
right = Vec(1, 0)
left = Vec(-1, 0)
up = Vec(0, -1)
down = Vec(0, 1)
vertical_moves = [up, down]
    
def check(pos, dir):
    newBoxes = []
    if pos + dir in walls or pos + dir + right in walls:
        return False, newBoxes
    if pos + dir in boxes:
        return True, [pos+dir]
    if pos + dir + right in boxes:
        newBoxes.append(pos+dir+right)
    if pos + dir + left in boxes:
        newBoxes.append(pos+dir+left)
    return True, newBoxes
        
def move_box_vert(pos, dir):
    to_check = [pos]
    to_move = []
    while to_check:
        nextBox = to_check.pop()
        to_move.append(boxes[boxes.index(nextBox)])
        can_move, newBoxes = check(nextBox, dir)
        if not can_move:
            return False
        to_check.extend(newBoxes)
        to_move.extend(newBoxes)
    [box.update(dir) for box in to_move]
    return True
    
        
def move_box_hor(pos, dir):
    to_move = []
    cur = pos
    while cur not in walls:
        if cur in boxes:
            to_move.append(boxes[boxes.index(cur)])
            cur += dir*2
        else: # free space -> update all boxes
            [box.update(dir) for box in to_move]
            return True
    return False

def move_box(pos, dir):
    if dir in vertical_moves:
        return move_box_vert(pos, dir)
    else:
        return move_box_hor(pos, dir)
# dh = display(print_field2(rob, boxes, shape), display_id=True, 
for move in instructions:
    dir = instr_map[move]
    newPos = rob + dir
    can_move = False
    if newPos in boxes:
        can_move = move_box(newPos, dir)
    elif newPos+left in boxes:
        can_move = move_box(newPos+left, dir)
    elif newPos not in walls:
        can_move = True
    if can_move:
        rob = newPos
    x = input()
    if x == 'x':
        break
    # clear_output(wait=True)
    print(print_field2(rob, boxes, walls, shape, symbol=move))
    # sleep(.2)

print(print_field2(rob, boxes, walls, shape, symbol=move))
x, y = np.where(field == '[')
sum(x + 100 * y)