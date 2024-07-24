from scipy.optimize import linear_sum_assignment


def hungarian_algorithm(cost_matrix):
    """
    Solve the assignment problem using the Hungarian algorithm.

    This function takes a cost matrix as input and returns the optimal assignment
    of rows to columns, minimizing the total cost. It utilizes the `linear_sum_assignment`
    function from SciPy's optimize module to perform the computation.

    Parameters:
    - cost_matrix (array_like): The cost matrix where each element represents the cost
      of assigning the row to the column. The matrix must be square or rectangular.

    Returns:
    - list of tuples: A list where each tuple contains the indices of the assigned row
      and column in the format (row_index, column_index).
    """
    # Using SciPy's linear_sum_assignment to solve the assignment problem
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    return list(zip(row_ind, col_ind))
