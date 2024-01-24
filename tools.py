import numpy as np
from typing import Sequence, Mapping

def mat_str(mat):
    original = str(mat)
    tmp = original.replace("], [", "],  [")
    return tmp.replace("], ", "],\n")
    

class MyMatrix():
    def __init__(self, mat: Sequence[Sequence[int]]):
        if mat is None:
            raise ValueError("null matrix")
        self.m = len(mat)
        if mat[0] is None:
            raise ValueError("null row")
        self.n = len(mat[0])
        for row in mat:
            if len(row) != self.n:
                raise ValueError("shape if not a matrix")    
        for i in range(self.m):
            for j in range(self.n):
                if mat[i][j] != 0 and mat[i][j] != 1:
                    raise ValueError("not binary")
        self.mat = list(mat)

    def __str__(self):
        return mat_str(self.mat)
    
    def dimensions(self):
        return (self.m, self.n)
    
    def real_rank(self):
        return np.linalg.matrix_rank(np.array(self.mat))
    
class RectangularPartition():
    def __init__(
            self,
            mat: Sequence[Sequence[int]],
            rectangles: Sequence[Mapping[str, Sequence[int]]]
            ):
        self.mat = MyMatrix(mat)
        (m, n) = self.mat.dimensions()
        reconstructed_mat = [[0 for _ in range(n)] for _ in range(m)]
        for rect in rectangles:
            for row in rect["rows"]:
                if row not in range(m):
                    raise ValueError(f"row {row} not in range")
                for col in rect["cols"]:
                    if col not in range(n):
                        raise ValueError(f"col {col} not in range")
                    reconstructed_mat[row][col] += 1
        for i in range(m):
            for j in range(n):
                if reconstructed_mat[i][j] != mat[i][j]:
                    raise ValueError("Rectangular partition invalid")
        self.rectangles = rectangles

    def visualize(self):
        print("-------------------original matrix-------------------")
        print(mat_str(self.mat.mat))
        for i, rect in enumerate(self.rectangles):
            print(f"-------------------rectangle {i}-------------------")
            (m, n) = self.mat.dimensions()
            rect_mat = [[0 for _ in range(n)] for _ in range(m)]
            for row in rect["rows"]:
                for col in rect["cols"]:
                    rect_mat[row][col] += 1
            print(mat_str(rect_mat))
        print(f"-------------------{len(self.rectangles)} rectangles in total")

