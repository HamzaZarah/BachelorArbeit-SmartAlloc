import json

def load_and_preprocess_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    students = data['students']
    timeslots = data['timeslots']
    # language_preferences = {student_id: details['language'] for student_id, details in students.items()}

    # Convert preferences (0, 1, 2) to availability (0, 1, 1)
    # availability = {}
    # for student_id, details in students.items():
        # preferences = details['slot']
        # Check if all preferences are 0
        # if all(pref == 0 for pref in preferences.values()):
            # Set all preferences to 1 if they are all 0
            # availability[student_id] = {slot: 1 for slot in preferences.keys()}
        # else:
            # availability[student_id] = {slot: 1 if pref > 0 else 0 for slot, pref in preferences.items()}

    availability = {}
    for student_id, details in students.items():
        preferences = details['slot']
        if all(pref == 0 for pref in preferences.values()):
            # Setzen aller Präferenzen auf 2, wenn sie alle 0 sind
            availability[student_id] = {slot: 2 for slot in preferences.keys()}
        else:
            availability[student_id] = {slot: (2 if pref == 2 else 1 if pref == 1 else 0) for slot, pref in
                                        preferences.items()}



    num_students = len(students)
    return students, timeslots, availability, num_students #, language_preferences




