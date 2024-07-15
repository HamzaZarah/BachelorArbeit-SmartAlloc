from data_loader import load_and_preprocess_data
from solver import create_solver, define_variables, define_constraints, define_objective
from ortools.linear_solver import pywraplp


def main():
    # Use the correct path to your JSON file
    benchmark_file = '/Users/hamzazarah/Desktop/Bachelor Arbeit/Daten/Benchmarks/benchmarks/n200-s11-01'

    students, timeslots, availability, num_students = load_and_preprocess_data(benchmark_file)

    # Print the loaded data to check the inputs
    print("Students:")
    for student_id, details in students.items():
        print(f"{student_id}: {details}")

    print("\nTimeslots:")
    for timeslot, details in timeslots.items():
        print(f"{timeslot}: {details}")

    print("\nAvailability:")
    for student_id, slots in availability.items():
        print(f"{student_id}: {slots}")

    print(f"\nNumber of Students: {num_students}")

    solver = create_solver()
    if solver:
        x = define_variables(solver, students, timeslots, availability)
        define_constraints(solver, x, students, timeslots, availability, num_students)
        define_objective(solver, x, students, timeslots)

        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            print('Optimal solution found:')
            for student in students:
                for slot in timeslots:
                    if x[student, slot].solution_value() > 0.5:
                        print(f'Student {student} is assigned to {slot}')
        else:
            print('No optimal solution found.')

        # Output of the variable values
        print("\nVariable values:")
        for student in students:
            for slot in timeslots:
                print(f"x_{student}_{slot}: {x[student, slot].solution_value()}")


if __name__ == "__main__":
    main()