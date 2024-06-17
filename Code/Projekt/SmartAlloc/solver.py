from ortools.linear_solver import pywraplp


def create_solver():
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return None
    return solver


def define_variables(solver, students, timeslots, availability):
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
        solver.Add(solver.Sum([x[student, slot] for slot in timeslots]) <= 1)


def define_objective(solver, x, students, timeslots):
    solver.Maximize(solver.Sum([x[student, slot] for student in students for slot in timeslots]))