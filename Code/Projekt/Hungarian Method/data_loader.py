import json
import numpy as np

def load_and_preprocess_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    students = data['students']
    timeslots = data['timeslots']

    num_students = len(students)
    num_slots = len(timeslots)

    # Calculate number of sub-slots per timeslot
    slots_per_timeslot = num_students // num_slots
    remaining_students = num_students % num_slots

    # Create an expanded timeslot list
    expanded_timeslots = []
    for slot in timeslots:
        for i in range(slots_per_timeslot):
            expanded_timeslots.append(f"{slot}_{i + 1}")
        if remaining_students > 0:
            expanded_timeslots.append(f"{slot}_{slots_per_timeslot + 1}")
            remaining_students -= 1

    cost_matrix = np.zeros((num_students, len(expanded_timeslots)))

    student_ids = list(students.keys())
    timeslot_ids = expanded_timeslots

    # Fill the cost matrix based on student preferences
    for i, student in enumerate(student_ids):
        preferences = students[student]['slot']
        for j, slot in enumerate(timeslot_ids):
            original_slot = '_'.join(slot.split('_')[:-1])
            pref_value = preferences.get(original_slot, 0)
            cost_matrix[i, j] = 1 if pref_value == 0 else 0

    return students, timeslots, cost_matrix, student_ids, timeslot_ids

# Beispielhafte Verwendung des Codes
if __name__ == "__main__":
    benchmark_file = '/Users/hamzazarah/Desktop/Bachelor Arbeit/Daten/Benchmarks/benchmarks/n50-s11-01'
    students, timeslots, cost_matrix, student_ids, timeslot_ids = load_and_preprocess_data(benchmark_file)

    #np.set_printoptions(threshold=np.inf)

    print("Cost Matrix:")
    print(cost_matrix)
    print("Student IDs:", student_ids)
    print("Timeslot IDs:", timeslot_ids)


