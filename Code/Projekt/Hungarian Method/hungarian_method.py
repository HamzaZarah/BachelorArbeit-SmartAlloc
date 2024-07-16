from scipy.optimize import linear_sum_assignment

def hungarian_algorithm(cost_matrix):
    # Using SciPy's linear_sum_assignment to solve the assignment problem
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    return list(zip(row_ind, col_ind))
