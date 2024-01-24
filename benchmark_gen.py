import random
import numpy as np
import json
import math

def rand_matrix(M, N, p):
    return [
        [1 if random.randint(0, 10000) < p*10000 else 0 for _ in range(N)]
        for _ in range(M)]

def generate_random_benchmark(M, N, density_list, mat_each_density=10):
    m_list=[]
    for i in density_list:
        count = 0
        while count < mat_each_density:
            mat = np.array(rand_matrix(M, N, i))
            if not any([(mat == m).all() for m in m_list]):
                if mat.sum() == int(i * M * N):
                    m_list.append(mat.tolist())
                    count += 1
    return m_list

def matrix_with_known_optimal(M, N, R):

    def generate_independent_vecs(vec_len, num_vec):
        vecs = []
        while len(vecs) < num_vec:
            vec = (np.random.rand(vec_len) > 0.5).astype(int)
            if np.linalg.matrix_rank(vecs + [vec, ]) > np.linalg.matrix_rank(vecs):
                vecs.append(vec)
        return vecs
    
    def generate_disjoint_vecs(vec_len, num_vec):
        vecs = [np.zeros(vec_len) for _ in range(num_vec)]
        choices = random.sample(list(range(vec_len)), num_vec)
        for i, vec in enumerate(vecs):
            vec[choices[i]] = 1
        for j in range(vec_len):
            if j not in choices:
                k = random.randint(0, num_vec + 1)
                if k < num_vec:
                    vecs[k][j] = 1
        return vecs


    if R > min(M, N):
        raise ValueError("required rank is too large for matrix dimensions")
    
    rows = [np.matrix(v) for v in generate_disjoint_vecs(N, R)]
    cols = [np.matrix([v,]).T for v in generate_independent_vecs(M, R)]
    mat = np.zeros((M, N))
    for i in range(R):
        mat += cols[i] * rows[i]

    return mat

def generate_benchmark_optimality(M, N, ranks, mat_per_rank=10):
    m_list=[]
    for r in ranks:
        count = 0
        while count < mat_per_rank:
            mat = np.array(matrix_with_known_optimal(M, N, r))
            if not any([(mat == m).all() for m in m_list]):
                m_list.append(mat.tolist())
                count += 1
    return m_list

def matrix_with_rank_gap(M, N, num_row_pairs):

    def create_pairs(set_ones, num_pairs):
        halfs = []
        while len(halfs) < num_pairs:
            half = random.sample(set_ones, random.randint(1, int(len(set_ones) / 2)))
            if not any([set(half) == set(h) for h in halfs]):
                halfs.append(half)
        return [(half, [x for x in set_ones if x not in half]) for half in halfs]

    if num_row_pairs * 2 > M:
        raise ValueError("not enough rows for required row pairs")
    num_of_ones = max(
        math.ceil( np.sqrt( 1 + 4 * (num_row_pairs - 1) ) ) + 1,
        num_row_pairs + 1
    )
    num_of_ones = random.randint(num_of_ones, N)
    main_vec_ones = random.sample(list(range(N)), num_of_ones)
    row_pairs = create_pairs(main_vec_ones, num_row_pairs)
    mat = []
    for v0, v1 in row_pairs:
        mat.append([1 if j in v0 else 0 for j in range(N)])
        mat.append([1 if j in v1 else 0 for j in range(N)])
    
    mat += rand_matrix(M - 2 * num_row_pairs - 1, N, 0.5)

    return np.array(mat)

def generate_benchmark_gap(M, N, num_pairs, num=100):
    m_list=[]
    count = 0
    while count < num:
        mat = np.array(matrix_with_rank_gap(M, N, num_pairs))
        if not any([(mat == m).all() for m in m_list]):
            m_list.append(mat.tolist())
            count += 1
    return m_list

if __name__ == "__main__":

    with open('benchmark_random_10x10.json', 'w') as f:
        json.dump(
            generate_random_benchmark(10, 10, [i/10 for i in range(1, 10)]),
            f,
        )
    with open('benchmark_random_10x20.json', 'w') as f:
        json.dump(
            generate_random_benchmark(10, 20, [i/10 for i in range(1, 10)]),
            f,
        )
    with open('benchmark_random_10x30.json', 'w') as f:
        json.dump(
            generate_random_benchmark(10, 30, [i/10 for i in range(1, 10)]),
            f,
        )
    with open('benchmark_random_100x100.json', 'w') as f:
        json.dump(
            generate_random_benchmark(100, 100, [0.01, 0.02, 0.05, 0.1, 0.2]),
            f,
        )
    with open('benchmark_optimality_10x10.json', 'w') as f:
        json.dump(
            generate_benchmark_optimality(10, 10, list(range(1, 11))),
            f,
        )
    with open('benchmark_gap_10x10_5.json', 'w') as f:
        json.dump(
            generate_benchmark_gap(10, 10, 5),
            f,
        )
    with open('benchmark_gap_10x10_4.json', 'w') as f:
        json.dump(
            generate_benchmark_gap(10, 10, 4),
            f,
        )
    with open('benchmark_gap_10x10_3.json', 'w') as f:
        json.dump(
            generate_benchmark_gap(10, 10, 3),
            f,
        )
    with open('benchmark_gap_10x10_2.json', 'w') as f:
        json.dump(
            generate_benchmark_gap(10, 10, 2),
            f,
        )
