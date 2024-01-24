# Exact Binary Matrix Factorization

This project provides SMT solving method and a heuristic, *row packing*, for the exact binary matrix factorization (EBMF) problem.
Additionally, we provide an SMT method to find fooling set size of a binary matrix.
To cite this work, please use the following bibtex entry.
```bibtex
@inproceedings{tan-ping-cong_date24_ebmf,
  title = {Depth-Optimal Addressing of {2D} Qubit Array with {1D} Controls Based on Exact Binary Matrix Factorization},
  author = {Tan, Daniel Bochen and Ping, Shuohao and Cong, Jason},
  booktitle = {Proceedings of the 27th Design, Automation and Test in Europe Conference},
  series = {{DATE} '24},
  year = {2024},
  month = mar,
  address = {Valencia, Spain},
  numpages = {6}
}
```

## Definition

Given a *m*-by-*n* binary matrix *M*, an exact binary matrix factorization is *M=HW* where *H* is a *m*-by-*r* binary matrix and *W* is a *r*-by-*n* binary matrix.
The minimum *r* such that this holds is called the *binary rank* of *M*.
Note that here the addition here is in the real field, not in the binary field.
For example,
```plain
1 1     1 1 0
0 1  *  1 0 1
1 0
```
is not an EBMF of
```plain
0 1 1
1 0 1
1 1 0
```
because the top left entry should 2, not 0, with addition in the real field.
A valid EBMF is
```
0 1 1     1 0 0
1 0 1  *  0 1 0
1 1 0     0 0 1
```
where *H* is the original matrix and *W* is identity, so this example is trivial.

*HW* can be written as the sum of *r* rank-1 matrices.
In the above example,
```plain
0 1 1     0 0 0     0 1 0     0 0 1
1 0 1  =  1 0 0  +  0 0 0  +  0 0 1
1 1 0     1 0 0     0 1 0     0 0 0
```
Each of the rank-1 matrix is 1 on a *(combinatorial) rectangle* which is a product of a set of rows and columns.
The rectangle corresponding to the second rank-1 matrix spans the second column, and the first and the third rows.

## Background
The EBMF problem appears in a few contexts.
In neutral atom arrays based quantum computing, some transitions can be induced by acousto-optic deflector (AOD) that illuminates some rows and columns.
To address an arbitrary 2D pattern of sites, we can use the AOD to illuminate sites at the intersections of some rows and columns each time.
The full pattern may need to be addressed in a few layers.
Each layer correspond to a rectangle in the EBMF.

In communication complexity theory, let the matrix represent the function *f* Alice and Bob want to compute.
The binary rank is the number of *f*-monochromatic rectangles to partition the 1's in *f*.
In communication complexity, we also care about partitioning the 0's.
The total number of *f*-monochromatic rectangles to partition *f* is a lower bound for communication complexity.
For an introduction, refer to the first chapter of [Kushilevitz&Nisan](https://doi.org/10.1017/CBO9780511574948).

EBMF are equivalent to a few other problems.
The binary matrix can be seen as the adjacency matrix of a bipartite graph, and each of the rank-1 matrix is a *biclique*, i.e., complete bipartite graph.
Thus, EBMF is equivalent to partition the edges of a bipartite graph to bicliques.
The decision version of EBMF is originally proven to be NP-complete by [Jiang&Ravikumar](https://doi.org/10.1007/3-540-54233-7_169).
Their description of the problem is called *normal set basis* problem.
For some examples, refer to our paper.

## Using the software

The main branch of this repo contains `tools.py` that provides some tool classes; `heuristics.py` that contains two heuristics: trivial and row packing; and `smt_solver.py` that contains the SMT-based method.
For original data and benchmarks in papers, refer to the corresponding branches.
The software depends on `numpy` and `z3-solver`.
We used `numpy==1.26.3` and `z3-solver==4.12.1.0` specifically.
We walk over an example below.

```python
mat = [
    [1, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 1, 1],
    [1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1],
    [1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1]
]

from heuristics import trivial_partition, row_packing_partition

trivial_ebmf = trivial_partition(mat)
print(trivial_ebmf)
```

The returned result is a `list` of `dict`s.
```bash
[
    {'rows': [0, 2, 4], 'cols': [0, 2]},
    {'rows': [1, 3, 4], 'cols': [1]},
    {'rows': [0, 3, 5], 'cols': [3]},
    {'rows': [1, 2, 5], 'cols': [4]},
    {'rows': [1, 3, 5], 'cols': [5]}
]
```
Each `dict` contains two keys `rows` and `cols`.
The values are `list`s of integers.


The meaning of this result is evident with a tool class `RectangularPartition`.
For example, the first one `{'rows': [0, 2, 4], 'cols': [0, 2]}` means a rank-1 matrix where the 1's are at rows 0, 2, 4, and columns 0 and 2.
```python
from tools import RectangularPartition

RectangularPartition(mat, trivial_ebmf).visualize()
```

The output should read
```bash
-------------------original matrix-------------------
[[1, 0, 1, 1, 0, 0],
 [0, 1, 0, 0, 1, 1],
 [1, 0, 1, 0, 1, 0],
 [0, 1, 0, 1, 0, 1],
 [1, 1, 1, 0, 0, 0],
 [0, 0, 0, 1, 1, 1]]
-------------------rectangle 0-------------------
[[1, 0, 1, 0, 0, 0],
 [0, 0, 0, 0, 0, 0],
 [1, 0, 1, 0, 0, 0],
 [0, 0, 0, 0, 0, 0],
 [1, 0, 1, 0, 0, 0],
 [0, 0, 0, 0, 0, 0]]
-------------------rectangle 1-------------------
[[0, 0, 0, 0, 0, 0],
 [0, 1, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0],
 [0, 1, 0, 0, 0, 0],
 [0, 1, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0]]
-------------------rectangle 2-------------------
[[0, 0, 0, 1, 0, 0],
 [0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0],
 [0, 0, 0, 1, 0, 0],
 [0, 0, 0, 0, 0, 0],
 [0, 0, 0, 1, 0, 0]]
-------------------rectangle 3-------------------
[[0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 1, 0],
 [0, 0, 0, 0, 1, 0],
 [0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 1, 0]]
-------------------rectangle 4-------------------
[[0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 1],
 [0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 1],
 [0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 1]]
-------------------5 rectangles in total
```

Another heuristic is row packing.
```python
rowpacking_ebmf = row_packing_partition(mat, 10)
```
The return format is the same.
The second argument is the number of trials to run the row packing heuristic.
Each time, the heuristic is run on `mat` with a randomly shuffled row ordering.
The heuristic is run on both the original matrix and the transposed matrix.

The SMT method can be used like
```python
from smt_solver import smt_euf_partition

smt_ebmf = smt_euf_partition(mat, known_solution=trivial_ebmf, if_print=True)
```
The second argument `known_solution` is optional.
We used `trivial_ebmf` here, but any valid solution is fine.
Suppose the binary rank of this solution is *r*, the SMT will initiates with *r*-1.
If this argument is not provided, the SMT would start with the solution returned by `row_packing_partition(mat, 10)`. 
The third argument `if_print` is also default to `False`.
In this example, apart from the `RectangularPartition` printout above, there will be
```bash
------------------------------------------------------
-------------------trying rank=4 with SAT
-------------------rank=4 UNSAT
```
It appears that the SMT method tried to find an EBMF with binary rank 4, but the formula is not satisfiable, so it proved the known solution is already optimal.

## Fooling set size
In our case, a fooling set is defined to be a set of 1's such that for each pair (i,j) and (i',j'), either (i,j') is 0 or (i',j) is 0 in the matrix.
Our SMT method returns the answer of 'given *M* and *b*, whether there is a fooling set of *M* with size >= *b*'.

```python
from smt_solver import fooling_set

print(fooling_set(mat, 5))
print(fooling_set(mat, 6))
```
The printout should be `True` and then `False`.
This means the matrix has a size-5 fooling set but not size-6.

## Acknowledgements
The DATE'24 paper is funded by NSF grant 442511-CJ-22291.
The authors would like to thank D. Bluvstein and H. Zhou for conversations on neutral atom arrays, and [a post on TCS Stack Exchange](https://cstheory.stackexchange.com/questions/34838/binary-rank-of-binary-matrix) about binary rank by D. Issac, R. Kothari, and S. Nikolov.