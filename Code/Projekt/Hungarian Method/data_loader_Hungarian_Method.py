#! /usr/bin/env python

import json
import numpy as np
import itertools
import os


def load_and_preprocess_data(file_path):
    """
    Load data from a JSON file and preprocess it for the scheduling problem.

    This function reads a JSON file containing information about students and timeslots,
    calculates the number of sub-slots per timeslot based on the number of students and timeslots,
    and expands the timeslot list accordingly. It returns the processed data including
    students, timeslots, student IDs, timeslot IDs, and expanded timeslots.

    Parameters:
    - file_path (str): The path to the JSON file containing the input data.

    Returns:
    - tuple: A tuple containing:
        - students (dict): A dictionary of students.
        - timeslots (list): A list of original timeslots.
        - student_ids (list): A list of student IDs.
        - timeslot_ids (list): A list of expanded timeslot IDs.
        - expanded_timeslots (list): A list of expanded timeslots.
    """
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

    # Update preferences: Set all preferences to 2 if they are all 0
    for student_id, details in students.items():
        preferences = details['slot']
        if all(pref == 0 for pref in preferences.values()):
            students[student_id]['slot'] = {slot: 2 for slot in preferences.keys()}

    return students, timeslots, student_ids, timeslot_ids, expanded_timeslots


def generate_cost_matrix(students, timeslot_ids, language_combination, expanded_timeslots, timeslots):
    """
    Generate a cost matrix for the scheduling problem based on student preferences and language combinations.

    This function creates a cost matrix where each element represents the cost of assigning a student
    to a timeslot, taking into account both slot preferences and language preferences. The cost is increased
    significantly if a preference is not met.

    Parameters:
    - students (dict): A dictionary of students with their preferences.
    - timeslot_ids (list): A list of expanded timeslot IDs.
    - language_combination (tuple): A tuple representing a specific combination of languages for the original timeslots.
    - expanded_timeslots (list): A list of expanded timeslots.
    - timeslots (list): A list of original timeslots.

    Returns:
    - numpy.ndarray: A 2D array representing the cost matrix.
    """
    num_students = len(students)
    cost_matrix = np.zeros((num_students, len(expanded_timeslots)))

    student_ids = list(students.keys())

    # Assign languages to original slots based on the language combination
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

    # Add costs based on language preferences
    for i, student in enumerate(student_ids):
        language_pref = students[student]['language']
        for j, slot in enumerate(timeslot_ids):
            original_slot = '_'.join(slot.split('_')[:-1])
            assigned_language = original_slot_languages[original_slot]
            lang_pref_value = language_pref.get(assigned_language, 0)
            # Increase the cost if the language preference is not met
            if lang_pref_value == 0:
                cost_matrix[i, j] += 100 * num_students
            elif lang_pref_value == 1:
                cost_matrix[i, j] += 1

        # Debug: Print the cost matrix for each combination
    # print(f"Cost Matrix for combination {language_combination}:")
    # print(cost_matrix)

    return cost_matrix


# Exemplary use of the code
if __name__ == "__main__":
    benchmark_file = os.path.join(os.path.expanduser('~'), 'Desktop', 'Bachelor Arbeit', 'Code', 'Projekt', 'benchmarks',
                                  'n100-s11-01')
    students, timeslots, student_ids, timeslot_ids, expanded_timeslots = load_and_preprocess_data(benchmark_file)
    language_combinations = list(itertools.product(['E', 'G'], repeat=len(timeslots)))
    np.set_printoptions(threshold=np.inf)
    np.set_printoptions(suppress=True)

    print("Student IDs:", student_ids)
    print("Timeslot IDs:", timeslot_ids)
    # print("Number of students:", len(students))

    for combination in language_combinations:
        cost_matrix = generate_cost_matrix(students, timeslot_ids, combination, expanded_timeslots, timeslots)
        print(f"Cost Matrix for combination {combination}:")
        print(cost_matrix)


