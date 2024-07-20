from ortools.linear_solver import pywraplp


def create_solver():
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return None
    return solver


def define_variables(solver, students, timeslots):
    x = {}
    for student in students:
        for slot in timeslots:
            x[student, slot] = solver.BoolVar(f'x_{student}_{slot}')
    return x


def define_constraints(solver, x, students, timeslots, availability, num_students, language_preferences):
    # Set capacity per slot based on the number of students divided by the number of slots
    capacity_per_slot = num_students // len(timeslots)
    capacities = {slot: capacity_per_slot for slot in timeslots}

    remaining_students = num_students % len(timeslots)
    for i, slot in enumerate(timeslots):
        if i < remaining_students:
            capacities[slot] += 1

    for slot in timeslots:
        solver.Add(solver.Sum([x[student, slot] for student in students]) <= capacities[slot])

    for student in students:
        for slot in timeslots:
            solver.Add(x[student, slot] <= availability[student][slot])

    # for student in students:
        # for slot in timeslots:
            # if language_preferences[student][slot] == 0:
                # solver.Add(x[student, slot] == 0)

    for student in students:
        solver.Add(solver.Sum([x[student, slot] for slot in timeslots]) == 1)


# def define_objective(solver, x, students, timeslots, availability):
    # objective_terms = []
    # for student in students:
        # for slot in timeslots:
            # availability_score = availability[student][slot]
            # weight = 1 if availability_score == 1 else 2 if availability_score == 2 else 0
            # objective_terms.append(weight * x[student, slot])
    # solver.Maximize(solver.Sum(objective_terms))


def define_objective(solver, x, students, timeslots, availability, language_preferences, group_preferences):
    objective_terms = []
    penalty_terms = []
    group_bonus_terms = []
    num_students = len(students)
    penalty_factor = 100 * num_students

    for student in students:
        for slot in timeslots:
            availability_score = availability[student][slot]
            language_preference_score = language_preferences[student][slot]

            # Weighting based on preferences
            if availability_score == 0:
                penalty = penalty_factor
            elif availability_score == 1:
                penalty = 1
            else:
                penalty = 0

            if language_preference_score == 0:
                penalty += penalty_factor
            elif language_preference_score == 1:
                penalty += 1

            weight = 1 - penalty  # Maximize the preference
            objective_terms.append(weight * x[student, slot])

            # Add penalty terms for non-preferred assignments
            penalty_terms.append(penalty * x[student, slot])

    # Add group preference bonus terms
    for student in students:
        group_preference = group_preferences.get(student, [])
        for preferred_student in group_preference:
            if preferred_student in students:
                for slot in timeslots:
                    group_bonus_terms.append(0.1 * (x[student, slot] + x[preferred_student, slot]))

    solver.Maximize(solver.Sum(objective_terms) + solver.Sum(group_bonus_terms) - solver.Sum(penalty_terms))

    """ 
        for student in students:
        for slot in timeslots:
            availability_score = availability[student][slot]
            language_preference_score = language_preferences[student][slot]
            weight = language_preference_score * availability_score
            objective_terms.append(weight * x[student, slot])

            # Hinzufügen von Strafpunkten für nicht erfüllte Sprachpräferenzen
            if language_preference_score < 2:
                penalty = (2 - language_preference_score) * x[student, slot]
                penalty_terms.append(penalty)

    # Ziel ist es, die Summe der Gewichte zu maximieren und die Strafpunkte zu minimieren
    solver.Maximize(solver.Sum(objective_terms) - solver.Sum(penalty_terms)) 
    """

