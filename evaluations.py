import random
import numpy as np
import sys
import time
import json
import argparse
from smt_solver import smt_euf_partition, fooling_set
from heuristics import trivial_partition, row_packing_partition



def examples():

    mat = [
        [0, 0, 1, 1, 1, 1, 0, 0, 1, 0],
        [1, 0, 1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
        [1, 1, 0, 1, 1, 1, 0, 0, 1, 1],
        [1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
        [0, 0, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 1, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
        [0, 1, 0, 1, 1, 0, 0, 1, 0, 1]
    ]
    
    # 'largest rectangle first' is not optimal 
    mat = [
        [0, 0, 0, 0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 1],
    ]
    print(smt_euf_partition(mat, if_print=True))
    
    mat = [
        [0, 0, 0, 0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 1],
    ]
    print(smt_euf_partition(mat, if_print=True))

    # running example
    mat = [
        [1, 0, 1, 1, 0, 0], 
        [0, 1, 0, 0, 1, 1], 
        [1, 0, 1, 0, 1, 0], 
        [0, 1, 0, 1, 0, 1], 
        [1, 1, 1, 0, 0, 0], 
        [0, 0, 0, 1, 1, 1]
    ]
    rank = len(smt_euf_partition(mat, if_print=True)["sat"])
    print(f"Does it have fooling set of size {rank}?")
    print(fooling_set(mat, rank))

    mat = [
        [1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0], 
        [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0], 
        [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0], 
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    ]
    print(smt_euf_partition(mat, if_print=True))


    # fooling set != binary rank
    mat = [
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        [0, 1, 1, 1]
    ]
    rank = len(smt_euf_partition(mat, if_print=True)["sat"])
    print(f"Does it have fooling set of size {rank}?")
    print(fooling_set(mat, rank))

    mat = [
        [1, 1, 0], 
        [0, 1, 1], 
        [1, 1, 1]
    ]
    rank = len(smt_euf_partition(mat, if_print=True)["sat"])
    print(f"Does it have fooling set of size {rank}?")
    print(fooling_set(mat, rank))



def prod_structure_try():

    def rand_matrix(M, N, p):
        return [
            [1 if random.randint(0, 10000) < p*10000 else 0 for _ in range(N)]
            for _ in range(M)]

    # randomly generate A,B and see if rank(A)*rank(B)=rank(A tensor B)
    A = rand_matrix(4, 4, random.uniform(0.1, 0.9))
    B = rand_matrix(4, 4, random.uniform(0.1, 0.9))
    print('A')
    rank_A = len(smt_euf_partition(A)["sat"])
    if rank_A == np.linalg.matrix_rank(np.array(A)):
        return
    print('B')
    rank_B = len(smt_euf_partition(B)["sat"])
    if rank_B == np.linalg.matrix_rank(np.array(B)):
        return
    prod = np.kron(np.array(A), np.array(B))
    if np.linalg.matrix_rank(prod) == rank_A * rank_B:
        return
    print('AB')
    rank_AB = len(smt_euf_partition(prod.tolist())["sat"])
    if rank_AB != rank_A * rank_B:
        print(A)
        print(B)
        print(prod)
    print('')

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='F', type=str, help='containing benchmarks')
    parser.add_argument('--trials', type=int, default=100,
                        help='number of row packing trials')
    parser.add_argument('--suffix', help='suffix to file name', type=str, default='100')
    parser.add_argument('--smt', action='store_true')
    parser.add_argument('--partition', action='store_true')
    args = parser.parse_args()

    file_name = args.file
    with open(file_name, 'r') as f:
        mat_lst = json.load(f)

    with open(file_name.split('.')[0] + '_stats_' + args.suffix, 'w') as f:
        f.write("id, density, linear rank, best, packing, trivial, runtime\n")
    if args.partition:
        with open(file_name.split('.')[0] + '_partition_' + args.suffix + '.json', 'w') as f:
            json.dump([], f)

    for i, mat in enumerate(mat_lst):
        density = sum([sum(row) for row in mat]) / (len(mat) * len(mat[0]))
        linear_rank = np.linalg.matrix_rank(np.array(mat))
        trivial_len = len(trivial_partition(mat))
        if args.smt:
            packing_result = row_packing_partition(mat, trials=args.trials)
        else:
            packing_result = row_packing_partition(mat, trials=1)
        packing_len = len(packing_result)
        start_time = time.time()
        if args.smt:
            best_result = smt_euf_partition(mat, known_solution=packing_result)
        else:
            best_result = row_packing_partition(mat, trials=args.trials)
        best_len = len(best_result)
        best_runtime = float(time.time() - start_time)
        with open(file_name.split('.')[0] + '_stats_' + args.suffix, 'a') as f:
            f.write(f"{i}, {density}, {linear_rank}, {best_len}, {packing_len}, {trivial_len}, {best_runtime}\n")
        if args.partition:
            with open(file_name.split('.')[0] + '_partition_' + args.suffix + '.json', 'r') as f:
                existing = json.load(f)
            existing.append(best_result)
            with open(file_name.split('.')[0] + '_partition_' + args.suffix + '.json', 'w') as f:
                json.dump(existing, f)
        