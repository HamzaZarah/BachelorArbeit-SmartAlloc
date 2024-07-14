from data_loader import load_and_preprocess_data
from hungarian_method import HungarianAlgorithm
import numpy as np

def main():
    benchmark_file = '/Users/hamzazarah/Desktop/Bachelor Arbeit/Daten/Benchmarks/benchmarks/n50-s11-01'

    students, timeslots, cost_matrix, student_ids, timeslot_ids = load_and_preprocess_data(benchmark_file)

    # Print the loaded data to check the inputs
    print("Cost Matrix:")
    print(cost_matrix)

    hungarian = HungarianAlgorithm(cost_matrix)
    hungarian.solve()

    assignments = hungarian.solution.items()

    sorted_assignments = sorted(assignments, key=lambda x: student_ids[x[1]])

    print('Optimale Lösung gefunden:')
    slot_counts = {slot: 0 for slot in timeslot_ids}
    for slot_idx, student_idx in sorted_assignments:
        student = student_ids[student_idx]
        slot = timeslot_ids[slot_idx]
        slot_counts[slot] += 1
        print(f'Student {student} ist zugewiesen zu {slot}')

    print("\nAnzahl der Studenten pro Slot:")
    for slot, count in slot_counts.items():
        print(f'{slot}: {count} Studenten')


if __name__ == "__main__":
    main()