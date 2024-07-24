from data_loader import load_and_preprocess_data, generate_cost_matrix
from hungarian_method import hungarian_algorithm
import numpy as np
import itertools


def main():
    """
    Main function to find the optimal assignment of students to timeslots based on language combinations.

    This script loads student and timeslot data from a benchmark file, generates all possible language
    combinations for the timeslots, and uses the Hungarian algorithm to find the optimal assignment
    that minimizes the total cost. The cost matrix is generated based on the preferences of students
    for each language combination in each timeslot. The script outputs the optimal language combination
    and the assignment of students to timeslots with the minimum total cost.
    """
    # Path to the benchmark file containing student and timeslot data
    benchmark_file = '/Users/hamzazarah/Desktop/Bachelor Arbeit/Daten/Benchmarks/benchmarks/n50-s11-01'
    # Load data from the benchmark file and preprocess it
    students, timeslots, student_ids, timeslot_ids, expanded_timeslots = load_and_preprocess_data(benchmark_file)
    # Generate all possible language combinations for the timeslots
    language_combinations = list(itertools.product(['E', 'G'], repeat=len(timeslots)))

    # Set initial minimum cost to infinity and optimal assignment to None
    np.set_printoptions(suppress=True)
    min_cost = np.inf
    optimal_assignment = None
    optimal_combination = None

    # Iterate over all language combinations and find the optimal assignment
    for combination in language_combinations:
        # Generate the cost matrix for the current language combination
        cost_matrix = generate_cost_matrix(students, timeslot_ids, combination, expanded_timeslots, timeslots)
        # Use the Hungarian algorithm to find the optimal assignment
        assignments = hungarian_algorithm(cost_matrix)
        # Calculate the total cost of the assignment
        total_cost = sum(cost_matrix[row, col] for row, col in assignments)

        # Update the minimum cost and optimal assignment if the current assignment has lower cost
        if total_cost < min_cost:
            min_cost = total_cost
            optimal_assignment = assignments
            optimal_combination = combination

    # Output the optimal assignment and language combination
    print(f'Optimal assignment for language combination {optimal_combination} with total costs {min_cost}:')
    for student_idx, timeslot_idx in optimal_assignment:
        student = student_ids[student_idx]
        timeslot = timeslot_ids[timeslot_idx]
        print(f'Student {student} is assigned to the timeslot {timeslot}.')


if __name__ == "__main__":
    main()

