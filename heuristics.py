import numpy as np
from tools import MyMatrix, RectangularPartition
import random



# ========================trivial heuristic==================================

def trivial_partition(A):
    rect_by_row = trivial_row_partition(A)
    by_col = trivial_row_partition((np.array(A).T).tolist())
    rect_by_col = [
        {"rows": rect["cols"], "cols": rect["rows"]} for rect in by_col
    ]
    # RectangularPartition(mat, rect_by_row).visualize()
    # RectangularPartition(mat, rect_by_col).visualize()
    if len(rect_by_row) > len(rect_by_col):
        return rect_by_col
    
    return rect_by_row


def trivial_row_partition(A):

    def eq_row(a, b):
        if len(a) != len(b):
            return False
        for (x, y) in zip(a, b):
            if x != y:
                return False
        return True

    mat = MyMatrix(A)
    (M, N) = mat.dimensions()
    rectangles = []
    saved = []
    removed = []
    for i, row in enumerate(A):
        if sum(row) == 0:
            removed.append(i)
            continue
        for r, j in enumerate(saved):
            if eq_row(A[j], row):
                rectangles[r]["rows"].append(i)
                removed.append(i)
        if i not in removed:
            rectangles.append(
                {
                    "rows": [i,], 
                    "cols": [k for k in range(N) if row[k] == 1]
                }
            )
            saved.append(i)

    return rectangles



# ========================row packing heuristic===============================
def row_packing_partition(mat, trials):

    # def weight_preserving_shuffle_func(row, stride):
    # # sorting preserving weight ordering but adding noise
    #     # stride = 1 # if you want default ordering
    #     return sum(row) * stride + random.randrange(stride)
    
    # def partial_ordering(rows, rho):
    # # sorting with gaussan noise
    #     n = len(rows)
    #     noise = (1.0 - rho * rho)**0.5
    #     order_value = [rho * i + noise * n * random.uniform(0, 1) for i in range(n)]
    #     pairing = [(rows[i], order_value[i]) for i in range(n)]
    #     return [tpl[0] for tpl in sorted(pairing, key=lambda pair: pair[1])]
    
    num_row = len(mat)
    num_col = len(mat[0])
    best_result = [0 for _ in range(num_row)]
    for _ in range(trials):
        perm_row = list(range(num_row))
        perm_col = list(range(num_col))
        # completely random sorting
        random.shuffle(perm_row)
        random.shuffle(perm_col)
        
        # sorting preserving weight ordering but adding noise
        # perm = sorted(
        #     perm,
        #     key = lambda x: weight_preserving_shuffle_func(mat[x], num_row)
        # ) # permutation of rows while preserving ordering in weight
        
        # sorting with gaussan noise
        # perm = sorted(perm, key = lambda x: sum(mat[x]))
        # perm = partial_ordering(perm, val)

        # sorting with gaussan noise
        # gaussian = np.random.normal(loc=0, scale=1, size=repetition)
        # gaussian = np.absolute(gaussian)
        # vals = [1 - x if x < 1 else 0 for x in gaussian]
        
        rectangles = row_packing(mat, perm_row)
        by_col = row_packing((np.array(mat).T).tolist(), perm_col)
        if len(rectangles) > len(by_col):
            rectangles = [
                {"rows": rect["cols"], "cols": rect["rows"]} for rect in by_col
            ]
        # RectangularPartition(mat, rectangles).visualize()

        if len(best_result) >= len(rectangles):
            best_result = rectangles
        if len(best_result) == np.linalg.matrix_rank(mat):
            break
    
    return best_result

def row_packing(mat, perm):

    def row_reduction(new_row, existing_rows):
        decomp = []
        for i, row in enumerate(existing_rows):
            diff = [x - y for x, y in zip(new_row, row)]
            if all(ele == 0 or ele == 1 for ele in diff):
                # 1's in row is contained in new_row, otherwise there can be -1
                new_row = list(diff)
                decomp.append(i)
        return new_row, decomp

    num_row = len(mat)
    rectangles = []
    basis = []

    for i in range(num_row):
        residue, decomp = row_reduction(mat[perm[i]], basis)
        for row_id in decomp:
            rectangles[row_id]["rows"].append(perm[i])
        if any(ele == 1 for ele in residue):
            rows_residue = [perm[i], ]
            for j, existing_basis in enumerate(basis):
                updated_basis, if_contain = row_reduction(existing_basis, [residue,])
                if if_contain:
                    basis[j] = updated_basis
                    rectangles[j]["cols"] = [i for i, ele in enumerate(updated_basis) if ele == 1]
                    rows_residue += rectangles[j]["rows"]
            basis.append(residue)
            rectangles.append(
                {
                    "cols": [i for i, ele in enumerate(residue) if ele == 1],
                    "rows": rows_residue,
                }
            )

    return rectangles
