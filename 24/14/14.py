import sys

sys.path.append("..")

import numpy as np
from utils.utils import Matrix, Vec

with open("input.txt") as file:
    lines = file.read().split("\n")

class Robot:
    def __init__(self, p, v):
        self.p = p
        self.v = v
    def __repr__(self):
        return f"R(p={self.p}, v={self.v})"

def get_pos_after_sec(rob, sec, shape):
    return Robot((rob.p + rob.v * sec) % shape, rob.v)

def display_board(robots, shape):
    m = Matrix(np.full((shape.x, shape.y), "."))
    for robot in robots:
        m[robot.p] = "#"
    string = "\n".join(["".join(line) for line in m.tolist()])
    return string

robots = [
    Robot(Vec(int(px),int(py)), Vec(int(vx),int(vy)))
    for robot  in lines
    for p, v   in [robot.split(" ")]
    for px, py in [p.split("=")[1].split(",")]
    for vx, vy in [v.split("=")[1].split(",")]
]
shape = Vec(101, 103)
count = 0
i = 1
while i != 0:
    if x := input(f"{count}, steps: "):
        i = int(x)
    else: i = 1
    robots = [get_pos_after_sec(robot, i, shape) for robot in robots]
    count += i
    print(display_board(robots, shape))
