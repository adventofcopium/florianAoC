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
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __hash__(self):
        return hash(repr(self))
    
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
    @staticmethod
    def from_str(s:str):
        return Matrix(np.array(list(map(list, s.read().split("\n")))).T)