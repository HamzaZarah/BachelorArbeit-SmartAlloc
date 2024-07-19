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


def define_constraints(solver, x, students, timeslots, availability, num_students):
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

    for student in students:
        solver.Add(solver.Sum([x[student, slot] for slot in timeslots]) == 1)

    # for student in students:
        # for slot in timeslots:
            # assigned_language = language_combination[slot]  # Die dem Timeslot zugewiesene Sprache
            # if language_preferences[student][assigned_language] == 0:
                # Constraint hinzufügen, um sicherzustellen, dass der Student nicht einem Slot mit dieser Sprache zugewiesen wird
                # solver.Add(x[student, slot] == 0)


def define_objective(solver, x, students, timeslots, avalability):
    objectve_terms = []
    for student in students:
        for slot in timeslots:
            availability_score = avalability[student][slot]
            weight = 1 if availability_score == 1 else 2 if availability_score == 2 else 0
            objectve_terms.append(weight * x[student, slot])
    solver.Maximize(solver.Sum(objectve_terms))

# def define_objective_with_language_preference(solver, x, students, timeslots, availability, language_preferences, language_combination):
    # objective_terms = []
    # for student, slot in x:
        # slot_index = timeslots.index(slot)
        # language = language_combination[slot_index]
        # language_preference_score = language_preferences[student][language]
        # availability_score = availability[student][slot]
        # weight = language_preference_score * availability_score
        # objective_terms.append(weight * x[student, slot])
    # solver.Maximize(solver.Sum(objective_terms))