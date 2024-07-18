from data_loader import load_and_preprocess_data, generate_cost_matrix
from hungarian_method import hungarian_algorithm
import numpy as np
import itertools

def main():
    benchmark_file = '/Users/hamzazarah/Desktop/Bachelor Arbeit/Daten/Benchmarks/benchmarks/n50-s11-01'

    # students, timeslots, cost_matrix, student_ids, timeslot_ids = load_and_preprocess_data(benchmark_file)
    students, timeslots, student_ids, timeslot_ids, expanded_timeslots = load_and_preprocess_data(benchmark_file)
    language_combinations = list(itertools.product(['E', 'G'], repeat=len(timeslots)))

    # Print the loaded data to check the inputs
    # print("Cost Matrix:")
    # print(cost_matrix)
    min_cost = np.inf
    optimal_assignment = None
    optimal_combination = None

    for combination in language_combinations:
        cost_matrix = generate_cost_matrix(students, timeslot_ids, combination, expanded_timeslots, timeslots)
        assignments = hungarian_algorithm(cost_matrix)
        total_cost = sum(cost_matrix[row, col] for row, col in assignments)
        print(f"Cost Matrix for combination {combination}:")
        print(cost_matrix)

        if total_cost < min_cost:
            min_cost = total_cost
            optimal_assignment = assignments
            optimal_combination = combination

    print(f'Optimale Zuordnung für Sprachkombination {optimal_combination} mit Gesamtkosten {min_cost}:')
    for student_idx, timeslot_idx in optimal_assignment:
        student = student_ids[student_idx]
        timeslot = timeslot_ids[timeslot_idx]
        print(f'Student {student} wird dem Timeslot {timeslot} zugeordnet.')

    # assignments = hungarian_algorithm(cost_matrix)

    # sorted_assignments = sorted(assignments, key=lambda x: student_ids[x[0]])

    # print('Optimal solution found:')
    # slot_counts = {slot: 0 for slot in timeslot_ids}
    # for slot_idx, student_idx in sorted_assignments:
        # student = student_ids[student_idx]
        # slot = timeslot_ids[slot_idx]
        # slot_counts[slot] += 1
        # print(f'Student {student} is assigned to {slot}')

    # print("\nNumber of students per slot:")
    # for slot, count in slot_counts.items():
        # print(f'{slot}: {count} students')

if __name__ == "__main__":
    main()