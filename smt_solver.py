from heuristics import row_packing_partition
from tools import MyMatrix, RectangularPartition
import z3


def smt_euf_partition(A, known_solution=None, if_print=False):
    if known_solution:
        partition = known_solution
    else:
        partition = row_packing_partition(A, 10)

    if if_print:
        print("-------------------heuristic result-------------------")
        RectangularPartition(A, partition).visualize()
        print("------------------------------------------------------")
    b = len(partition) - 1
    mat = MyMatrix(A)
    real_rank = mat.real_rank()
    if real_rank == len(partition):
        return partition
    (M, N) = mat.dimensions()

    # construct SAT
    solver = z3.Solver()
    vars = {}
    num1 = 0
    for i in range(M):
        for j in range(N):
            if A[i][j] == 1:
                vars[(i,j)] = num1
                num1 += 1
    f = z3.Function(
        'rect',
        z3.BitVecSort(max(1, num1.bit_length())),
        z3.BitVecSort(max(1, b.bit_length()))
    )

    for i in range(num1):
        solver.add(z3.ULT(f(i), b))
    for i in range(M):
        for j in range(N):
            for ii in range(M):
                for jj in range(N):
                    if i != ii and j != jj and A[i][j] == 1 and A[ii][jj] == 1:
                        if A[i][jj] == 0:
                            solver.add(
                                z3.Not(f(vars[(i,j)]) == f(vars[(ii,jj)]))
                            )
                        if A[i][jj] == 1:
                            solver.add(
                                z3.Implies(
                                    f(vars[(i,j)]) == f(vars[(ii,jj)]),
                                    f(vars[(i,j)]) == f(vars[(i,jj)])
                                )
                            )

    while b >= real_rank:
        if if_print:
            print(f"-------------------trying rank={b} with SAT")
        check_result = solver.check()
        if check_result == z3.unsat:
            if if_print:
                print(f"-------------------rank={b} UNSAT")
            break
        elif check_result == z3.sat:
            model = solver.model()
            
            # readout solution 
            products = []
            for k in range(b):
                rows = []
                cols = []
                for i in range(M):
                    for j in range(N):
                        if A[i][j] == 1:
                            if model.evaluate(f(vars[(i,j)])) == k:
                                if i not in rows:
                                    rows.append(i)
                                if j not in cols:
                                    cols.append(j)
                products.append({"rows": rows, "cols": cols})
                partition = products
            if if_print:
                RectangularPartition(A, partition).visualize()
            
            b -= 1

            # narrow down the solution space
            for i in range(num1):
                solver.add(z3.ULT(f(i), b))
            
        else:
            raise ValueError("z3 not returning")
        
    return partition

def fooling_set(A, b):
    # check if A has fooling set with size >= b
    M, N = MyMatrix(A).dimensions()
    x = [[z3.Bool(f'in_row{m}_col{n}') for n in range(N)] for m in range(M)]
    solver = z3.Solver()
    for i in range(M):
        for j in range(N):
            if A[i][j] == 0:
                solver.add(z3.Not(x[i][j]))
    for i in range(M):
        for j in range(N):
            for ii in range(M):
                for jj in range(N):
                    if A[i][j] == 1 and A[ii][jj] == 1:
                        if i == ii and j == jj:
                            continue
                        if i == ii or j == jj:
                            solver.add(
                                z3.Or( z3.Not(x[i][j]), z3.Not(x[ii][jj]))
                            )
                            continue
                        if A[i][jj] ==1 and A[ii][j] == 1:
                            solver.add(
                                z3.Or( z3.Not(x[i][j]), z3.Not(x[ii][jj]))
                            )
    solver.add(
        b <= sum(
            [z3.If(x[i][j], 1, 0) for i in range(M) for j in range(N)]
        )
    )
    
    if solver.check() == z3.sat:
        return True
    else:
        return False