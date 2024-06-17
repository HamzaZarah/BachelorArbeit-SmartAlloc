import json
import os
from ortools.linear_solver import pywraplp


def load_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    with open(file_path, 'r') as file:
        return json.load(file)


def create_solver():
    return pywraplp.Solver.CreateSolver('SCIP')


def add_variables(solver, students, timeslots):
    x = {}
    for student in students:
        for slot in timeslots:
            x[student, slot] = solver.BoolVar(f'x_{student}_{slot}')
    return x


def add_constraints(solver, x, students, timeslots, timeslot_capacities, team_size):
    for student in students:
        solver.Add(sum(x[student, slot] for slot in timeslots) <= 1)

    for slot in timeslots:
        solver.Add(sum(x[student, slot] for student in students) <= timeslot_capacities[slot])

    # Add group constraints if team_size is defined
    if team_size:
        for student, details in students.items():
            group = details['group']
            if group:
                for slot in timeslots:
                    group_vars = [x[student_id, slot] for student_id in group]
                    solver.Add(solver.Sum(group_vars) == solver.Sum(x[student, slot]))


def set_objective(solver, x, students, timeslots):
    solver.Maximize(solver.Sum(x[student, slot] for student in students for slot in timeslots))


def main():
    # Pfad zur Benchmark-Datei definieren (Datei 'ads24.json' oder 'dmics23.json')
    benchmark_file = '/Users/hamzazarah/Desktop/Bachelor Arbeit/Daten/Benchmarks/benchmarks/ads24.json'  # oder '../../Daten/Benchmarks/benchmarks/dmics23.json'

    if not os.path.exists(benchmark_file):
        raise FileNotFoundError(f"The file {benchmark_file} does not exist. Please check the path.")

    # Daten laden
    data = load_data(benchmark_file)
    students = data['students']
    timeslots = set()
    for student_info in students.values():
        timeslots.update(student_info['slot'].keys())
    timeslots = list(timeslots)
    team_size = data.get('team_size', None)

    # Define timeslot capacities manually
    timeslot_capacities = {
        'Fr': 10,
        'Tu': 10,
        'We': 10,
        'We1': 10,
        'We2': 10,
        'We3': 10
    }

    # Präferenzen umwandeln
    for student_id, student_info in students.items():
        student_info['slot'] = {k: (1 if v > 0 else 0) for k, v in student_info['slot'].items()}
        student_info['language'] = {k: (1 if v > 0 else 0) for k, v in student_info['language'].items()}

    # Solver erstellen
    solver = create_solver()
    if not solver:
        raise Exception("Solver could not be created.")

    # Variablen definieren
    x = add_variables(solver, students, timeslots)

    # Constraints setzen
    add_constraints(solver, x, students, timeslots, timeslot_capacities, team_size)

    # Zielfunktion definieren
    set_objective(solver, x, students, timeslots)

    # Problem lösen
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Optimal solution found:')
        for student in students:
            for slot in timeslots:
                if x[student, slot].solution_value():
                    print(f'Student {student} assigned to timeslot {slot}')
    else:
        print('No optimal solution found.')


if __name__ == '__main__':
    main()



