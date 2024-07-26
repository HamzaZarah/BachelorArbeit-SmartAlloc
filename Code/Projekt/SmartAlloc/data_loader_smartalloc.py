#! /usr/bin/env python

import json


def load_and_preprocess_data(file_path):
    """
    Loads and preprocesses data from a JSON file.

    This function reads a JSON file specified by the file_path parameter, extracting information about students,
    timeslots, language preferences, group preferences, and availability for each student. It processes the availability
    data to ensure that all preferences are correctly represented as integers (0, 1, or 2), where necessary converting
    all-zero preferences to a default value.

    Args:
        file_path (str): The path to the JSON file containing the data.

    Returns:
        tuple: A tuple containing:
            - A dictionary of students.
            - A list of timeslots.
            - A dictionary mapping each student to their availability for each timeslot.
            - The total number of students.
            - A dictionary of language preferences for each student.
            - A dictionary of group preferences for each student.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)

    students = data['students']
    timeslots = data['timeslots']
    language_preferences = {student_id: details['language'] for student_id, details in students.items()}
    group_preferences = {student_id: details['group'] for student_id, details in students.items()}

    availability = {}
    for student_id, details in students.items():
        preferences = details['slot']
        if all(pref == 0 for pref in preferences.values()):
            # Set all preferences to 2 if they are all 0
            availability[student_id] = {slot: 2 for slot in preferences.keys()}
        else:
            availability[student_id] = {slot: (2 if pref == 2 else 1 if pref == 1 else 0) for slot, pref in
                                        preferences.items()}

    num_students = len(students)
    return students, timeslots, availability, num_students, language_preferences, group_preferences




