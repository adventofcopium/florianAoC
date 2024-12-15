import numpy as np


class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Vec(self.x - other.x, self.y - other.y)
    def __repr__(self):
        return f"Vec({self.x}, {self.y})"
    def __rshift__(self, k):
        return self if k == 0 else Vec(-self.y, self.x) >> k-1
    def __lshift__(self, k):
        return self if k == 0 else Vec(self.y, -self.x) << k-1
    def __mul__(self, other):
        return Vec(self.x * other, self.y * other)
    def __mod__(self, other):
        if isinstance(other, int):
            return Vec(self.x % other, self.y % other)
        elif isinstance(other, Vec):
            return Vec(self.x % other.x, self.y % other.y)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y
    def __hash__(self):
        return hash(repr(self))
    def get_neighbors(self, bound:"Matrix"=None):
        neighbors = [self + dir for dir in [Vec(0,1), Vec(-1,0), Vec(0,-1), Vec(1,0)]]
        return [nb for nb in neighbors if (nb in bound)] if bound is not None else neighbors
    def update(self, dir):
        self.x += dir.x
        self.y += dir.y
    
class Matrix(np.ndarray):
    def __new__(cls, input_array):
        return np.asarray(input_array).view(cls)
    def __getitem__(self, key):
        if isinstance(key, Vec):
            key = (key.x, key.y)
        return super().__getitem__(key)
    def __setitem__(self, key, value):
        if isinstance(key, Vec):
            key = (key.x, key.y)
        return super().__setitem__(key, value)
    def __contains__(self, pos):
        if isinstance(pos, Vec):
            m, n = self.shape
            return 0 <= pos.x < m and 0 <= pos.y < n
        return super().__contains__(pos)
    def __repr__(self):
        return np.ndarray.__repr__(self.T)
    def __str__(self):
        return "\n".join(["".join(line) for line in self.T.tolist()])
    @staticmethod
    def from_str(s:str):
        return Matrix(np.array(list(map(list, s.split("\n")))).T)