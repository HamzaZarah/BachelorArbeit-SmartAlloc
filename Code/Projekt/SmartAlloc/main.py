import itertools
from data_loader import load_and_preprocess_data
from solver import create_solver, define_variables, define_constraints, define_objective
from ortools.linear_solver import pywraplp


def adjust_language_preferences(original_preferences, language_combination, timeslots):
    adjusted_preferences = {}
    for student, preferences in original_preferences.items():
        adjusted_preferences[student] = {}
        for slot, language in zip(timeslots, language_combination):
            adjusted_preferences[student][slot] = preferences.get(language, 0)
    return adjusted_preferences


def main():
    # Use the correct path to your JSON file
    benchmark_file = '/Users/hamzazarah/Desktop/Bachelor Arbeit/Daten/Benchmarks/benchmarks/n50-s11-01'

    # students, timeslots, availability, num_students = load_and_preprocess_data(benchmark_file)
    students, timeslots, availability, num_students, language_preferences, group_preferences = load_and_preprocess_data(benchmark_file)

    # Print the loaded data to check the inputs
    # print("Students:")
    # for student_id, details in students.items():
        # print(f"{student_id}: {details}")

    # print("\nTimeslots:")
    # for timeslot, details in timeslots.items():
        # print(f"{timeslot}: {details}")

    # print("\nAvailability:")
    # for student_id, slots in availability.items():
        # print(f"{student_id}: {slots}")

    languages = ['E', 'G']
    best_solution_value = float('inf')
    best_combination = None
    best_assignment = []

    # print(f"\nNumber of Students: {num_students}")

    # solver = create_solver()
    # if solver:
        # x = define_variables(solver, students, timeslots)
        # define_constraints(solver, x, students, timeslots, availability, num_students)
        # define_objective(solver, x, students, timeslots, availability)

        # status = solver.Solve()

        # if status == pywraplp.Solver.OPTIMAL:
            # print('Optimal solution found:')
            # for student in students:
                # for slot in timeslots:
                    # if x[student, slot].solution_value() == 1:
                        # print(f'Student {student} is assigned to {slot}')
            # Zusätzliche Ausgabe: Anzahl der Studenten pro Timeslot
            # print('\nAnzahl der Studenten pro Timeslot:')
            # for slot in timeslots:
                # num_students_assigned = sum(x[student, slot].solution_value() for student in students)
                # print(f'Timeslot {slot}: {num_students_assigned} Student(en)')
        # else:
            # print('No optimal solution found.')

        # Output of the variable values
        # print("\nVariable values:")
        # for student in students:
            # for slot in timeslots:
                # print(f"x_{student}_{slot}: {x[student, slot].solution_value()}")

    for language_combination in itertools.product(languages, repeat=len(timeslots)):
        adjusted_language_preferences = adjust_language_preferences(language_preferences, language_combination,
                                                                    timeslots)

        solver = create_solver()
        if solver:
            x = define_variables(solver, students, timeslots)
            define_constraints(solver, x, students, timeslots, availability, num_students,
                               adjusted_language_preferences)
            define_objective(solver, x, students, timeslots, availability, adjusted_language_preferences,
                             group_preferences)
            status = solver.Solve()

            if status == pywraplp.Solver.OPTIMAL:
                solution_value = solver.Objective().Value()
                if solution_value < best_solution_value:
                    best_solution_value = solution_value
                    best_combination = language_combination
                    best_assignment = [(student, slot) for student in students for slot in timeslots if
                                       x[student, slot].solution_value() == 1]

    print(f'Beste Sprachkombination: {best_combination}')
    print('Optimale Zuweisung:')
    for student, slot in best_assignment:
        print(f'Student {student} ist dem Timeslot {slot} zugewiesen')

    print('\nAnzahl der Studenten pro Timeslot:')
    for slot in timeslots:
        num_students_assigned = sum(x[student, slot].solution_value() for student in students)
        print(f'Timeslot {slot}: {num_students_assigned} Student(en)')

    print(best_solution_value)


if __name__ == "__main__":
    main()