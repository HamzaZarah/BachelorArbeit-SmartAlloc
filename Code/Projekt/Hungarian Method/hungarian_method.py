import numpy as np


class HungarianAlgorithm(object):
    def __init__(self, cost_matrix):
        """
        Initializes the Hungarian Algorithm with the given cost matrix.

        Parameters:
        - cost_matrix (np.ndarray): The cost matrix for the assignment problem.
        """
        self.original_cost_matrix = cost_matrix
        self.cost_matrix = cost_matrix.copy()
        self.num_rows, self.num_cols = self.cost_matrix.shape
        self.row_covered = np.zeros(self.num_rows, dtype=bool)
        self.col_covered = np.zeros(self.num_cols, dtype=bool)
        self.marked_matrix = np.zeros((self.num_rows, self.num_cols), dtype=int)
        self.solution = None
        self.minimum_cost = None

    def _clear_covers(self):
        """Clears all row and column covers."""
        self.row_covered[:] = False
        self.col_covered[:] = False

    def _clear_marks(self):
        """Clears all marks in the marked matrix."""
        self.marked_matrix[:, :] = 0

    def solve(self):
        """
        Solves the assignment problem using the Hungarian Algorithm.

        Returns:
        - bool: True if a solution is found, False otherwise.
        """
        step = _step0
        if self.num_rows == self.num_cols:
            step = _step1

        while type(step) is not tuple:
            step = step(self)

        if step[0]:
            self.solution = step[2]
            self.minimum_cost = step[1]
        return step[0]

    def print_results(self):
        """Prints the results of the assignment problem."""
        if self.solution is None:
            raise Exception(
                "No solution was computed yet or there is no solution. Run the solve method or try another cost matrix.")
        for slot, student in self.solution.items():
            print(f"Student {student} is assigned to slot {slot}")
        print(f"The final total cost was {self.minimum_cost}")


def _step0(state):
    """
    Pads the cost matrix to make it square.

    Parameters:
    - state (HungarianAlgorithm): The current state of the algorithm.

    Returns:
    - function: The next step in the algorithm.
    """
    matrix_size = max(state.num_rows, state.num_cols)
    pad_columns = matrix_size - state.num_rows
    pad_rows = matrix_size - state.num_cols
    state.cost_matrix = np.pad(state.cost_matrix, ((0, pad_columns), (0, pad_rows)), 'constant', constant_values=(0))

    state.row_covered = np.zeros(state.cost_matrix.shape[0], dtype=bool)
    state.col_covered = np.zeros(state.cost_matrix.shape[1], dtype=bool)
    state.marked_matrix = np.zeros((state.cost_matrix.shape[0], state.cost_matrix.shape[1]), dtype=int)
    return _step1


def _step1(state):
    """
    Subtracts the minimum value in each row from all elements of that row.

    Parameters:
    - state (HungarianAlgorithm): The current state of the algorithm.

    Returns:
    - function: The next step in the algorithm.
    """
    state.cost_matrix -= np.min(state.cost_matrix, axis=1)[:, np.newaxis]
    return _step2


def _step2(state):
    """
    Subtracts the minimum value in each column from all elements of that column.

    Parameters:
    - state (HungarianAlgorithm): The current state of the algorithm.

    Returns:
    - function: The next step in the algorithm.
    """
    state.cost_matrix -= np.min(state.cost_matrix, axis=0)[np.newaxis, :]
    return _step3


def _step3(state):
    """
    Covers all zeros in the matrix using the minimum number of horizontal and vertical lines.
    If the minimum number of lines is equal to the size of the matrix, a solution is found.
    Otherwise, the algorithm proceeds to step 4.

    Parameters:
    - state (HungarianAlgorithm): The current state of the algorithm.

    Returns:
    - function: The next step in the algorithm or a tuple indicating the solution status.
    """
    row_marked = np.zeros(state.cost_matrix.shape[0], dtype=bool)
    col_marked = np.zeros(state.cost_matrix.shape[1], dtype=bool)

    for j in range(state.cost_matrix.shape[1]):
        for i in range(state.cost_matrix.shape[0]):
            if not state.row_covered[i] and not state.col_covered[j] and state.cost_matrix[i][j] == 0:
                state.marked_matrix[i][j] = 1
                state.row_covered[i] = True
                state.col_covered[j] = True

    state._clear_covers()

    for i in range(state.cost_matrix.shape[0]):
        if np.sum(state.marked_matrix[i, :]) == 0:
            row_marked[i] = True
            for j in range(state.cost_matrix.shape[1]):
                if not col_marked[j] and state.cost_matrix[i][j] == 0:
                    col_marked[j] = True
                    for k in range(state.cost_matrix.shape[0]):
                        if not row_marked[k] and state.marked_matrix[k][j] == 1:
                            row_marked[k] = True

    state.row_covered = np.logical_not(row_marked)
    state.col_covered = col_marked
    num_lines = np.sum(state.row_covered) + np.sum(state.col_covered)

    if num_lines == state.cost_matrix.shape[0]:
        sol = _check_for_solution(state)
        return sol
    else:
        return _step4


def _step4(state):
    """
    Modifies the cost matrix to create additional zeros.

    Parameters:
    - state (HungarianAlgorithm): The current state of the algorithm.

    Returns:
    - function: The next step in the algorithm.
    """
    smallest_uncovered = np.inf
    for i in range(state.cost_matrix.shape[0]):
        for j in range(state.cost_matrix.shape[1]):
            if not state.row_covered[i] and not state.col_covered[j] and state.cost_matrix[i][j] < smallest_uncovered:
                smallest_uncovered = state.cost_matrix[i][j]

    for i in range(state.cost_matrix.shape[0]):
        for j in range(state.cost_matrix.shape[1]):
            if not state.row_covered[i] and not state.col_covered[j]:
                state.cost_matrix[i][j] -= smallest_uncovered
            elif state.row_covered[i] and state.col_covered[j]:
                state.cost_matrix[i][j] += smallest_uncovered

    state._clear_covers()
    state._clear_marks()
    return _step3


def _check_for_solution(state):
    """
    Checks if a solution is found by using the marked zeros.

    Parameters:
    - state (HungarianAlgorithm): The current state of the algorithm.

    Returns:
    - tuple: A tuple indicating if a solution is found, the minimum cost, and the solution.
    """
    for j in range(state.cost_matrix.shape[1]):
        for i in range(state.cost_matrix.shape[0]):
            if not state.row_covered[i] and not state.col_covered[j] and state.cost_matrix[i][j] == 0:
                state.marked_matrix[i][j] = 1
                state.row_covered[i] = True
                state.col_covered[j] = True

    solution = {}
    cost = 0
    for i in range(state.num_rows):
        for j in range(state.num_cols):
            if state.marked_matrix[i][j] == 1:
                solution[j] = i
                cost += state.original_cost_matrix[i][j]

    state._clear_covers()
    return len(solution) == state.num_cols, cost, solution

