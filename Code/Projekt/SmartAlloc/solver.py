from ortools.linear_solver import pywraplp


def create_solver():
    """
    Creates a SCIP solver instance.

    Returns:
        A SCIP solver instance if successful, None otherwise.
    """
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return None
    return solver


def define_variables(solver, students, timeslots):
    """
    Defines boolean variables for each student and timeslot combination.

    Args:
        solver: The SCIP solver instance.
        students: A list of student identifiers.
        timeslots: A list of timeslot identifiers.

    Returns:
        A dictionary mapping (student, timeslot) pairs to SCIP boolean variables.
    """
    x = {}
    for student in students:
        for slot in timeslots:
            x[student, slot] = solver.BoolVar(f'x_{student}_{slot}')
    return x


def define_constraints(solver, x, students, timeslots, availability, num_students, language_preferences,
                       group_preferences):
    """
    Defines the constraints for the solver based on student availability, timeslot capacities,
    and language preferences.

    Args:
        solver: The SCIP solver instance.
        x: The dictionary of decision variables.
        students: A list of student identifiers.
        timeslots: A list of timeslot identifiers.
        availability: A dictionary mapping (student, timeslot) pairs to availability scores.
        num_students: The total number of students.
        language_preferences: A dictionary mapping (student, timeslot) pairs to language preference scores.
        group_preferences: A dictionary mapping students to lists of preferred group members.
    """
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
        for slot in timeslots:
            if language_preferences[student][slot] == 0:
                solver.Add(x[student, slot] == 0)

    for student, preferences in group_preferences.items():
        for peer in preferences:
            for slot in timeslots:
                solver.Add(x[student, slot] == x[peer, slot])

    for student in students:
        solver.Add(solver.Sum([x[student, slot] for slot in timeslots]) == 1)


def define_objective(solver, x, students, timeslots, availability, language_preferences):
    """
    Defines the objective function for the solver to maximize student preferences while minimizing penalties.

    Args:
        solver: The SCIP solver instance.
        x: The dictionary of decision variables.
        students: A list of student identifiers.
        timeslots: A list of timeslot identifiers.
        availability: A dictionary mapping (student, timeslot) pairs to availability scores.
        language_preferences: A dictionary mapping (student, timeslot) pairs to language preference scores.
    """
    # objective_terms = []
    penalty_terms = []
    num_students = len(students)
    penalty_factor = 100 * num_students

    for student in students:
        for slot in timeslots:
            availability_score = availability[student][slot]
            language_preference_score = language_preferences[student][slot]

            # Penalty based on preferences
            penalty = 0
            if availability_score == 0:
                penalty += penalty_factor
            elif availability_score == 1:
                penalty += 1

            if language_preference_score == 1:
                penalty += 1

            # Add penalty terms for non-preferred assignments
            penalty_terms.append(penalty * x[student, slot])

    solver.Minimize(solver.Sum(penalty_terms))


