import json
import numpy as np
import itertools

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

    student_ids = list(students.keys())
    timeslot_ids = expanded_timeslots

    return students, timeslots, student_ids, timeslot_ids, expanded_timeslots

def generate_cost_matrix(students, timeslot_ids, language_combination, expanded_timeslots, timeslots):
    num_students = len(students)
    cost_matrix = np.zeros((num_students, len(expanded_timeslots)))

    student_ids = list(students.keys())

    # Zuordnung von Sprachen zu original_slots basierend auf der language_combination
    original_slot_languages = {timeslot: lang for timeslot, lang in zip(timeslots.keys(), language_combination)}

    # Fill the cost matrix based on student preferences
    for i, student in enumerate(student_ids):
        preferences = students[student]['slot']
        for j, slot in enumerate(timeslot_ids):
            original_slot = '_'.join(slot.split('_')[:-1])
            pref_value = preferences.get(original_slot, 0)
            if pref_value == 0:
                cost_matrix[i, j] += 100 * num_students
            elif pref_value == 1:
                cost_matrix[i, j] += 1

    # Hinzufügen der Kosten basierend auf Sprachpräferenzen
    for i, student in enumerate(student_ids):
        language_pref = students[student]['language']
        for j, slot in enumerate(timeslot_ids):
            original_slot = '_'.join(slot.split('_')[:-1])
            assigned_language = original_slot_languages[original_slot]
            lang_pref_value = language_pref.get(assigned_language, 0)
            # Erhöhe die Kosten, wenn die Sprachpräferenz nicht erfüllt ist
            if lang_pref_value == 0:
                cost_matrix[i, j] += 100 * num_students
            elif lang_pref_value == 1:
                cost_matrix[i, j] += 1

    return cost_matrix


# Exemplary use of the code
if __name__ == "__main__":
    benchmark_file = '/Users/hamzazarah/Desktop/Bachelor Arbeit/Daten/Benchmarks/benchmarks/n50-s11-01'
    # students, timeslots, cost_matrix, student_ids, timeslot_ids = load_and_preprocess_data(benchmark_file)
    students, timeslots, student_ids, timeslot_ids, expanded_timeslots = load_and_preprocess_data(benchmark_file)

    language_combinations = list(itertools.product(['E', 'G'], repeat=len(timeslots)))

    # np.set_printoptions(threshold=np.inf)
    np.set_printoptions(suppress=True)

    # print("Cost Matrix:")
    # print(cost_matrix)
    print("Student IDs:", student_ids)
    print("Timeslot IDs:", timeslot_ids)
    # print("Number of students:", len(students))

    for combination in language_combinations:
        cost_matrix = generate_cost_matrix(students, timeslot_ids, combination, expanded_timeslots, timeslots)
        print(f"Cost Matrix for combination {combination}:")
        print(cost_matrix)


