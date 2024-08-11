#! /usr/bin/env python

import argparse
import itertools
import logging
import time
import os
from data_loader_smartalloc import load_and_preprocess_data
from solver import create_solver, define_variables, define_constraints, define_objective
from ortools.linear_solver import pywraplp


def is_combination_feasible(language_preferences, language_combination, timeslots):
    """
    Checks if a given language combination is feasible for all students across the specified timeslots.

    This function iterates through each timeslot and assigns the corresponding language from the language_combination.
    It then checks for each student if there is at least one timeslot where a preferred language is available.
    If any student does not have a preferred language available in any of the timeslots, the combination is deemed
    infeasible.

    Args:
        language_preferences (dict): A dictionary mapping each student to their language preferences.
                                     The preferences are represented as a dictionary of languages with their
                                     corresponding preference level.
        language_combination (tuple): A tuple representing the selected language for each timeslot.
        timeslots (list): A list of timeslots available for assignment.

    Returns:
        bool: True if the language combination is feasible for all students, False otherwise.
    """
    # Create a set of available languages for each slot
    available_languages_per_slot = {slot: set() for slot in timeslots}
    for slot, language in zip(timeslots, language_combination):
        available_languages_per_slot[slot].add(language)

    # Check for each student if at least one preferred language is available in any timeslot
    for student, preferences in language_preferences.items():
        if not any(preferences[language] > 0 for slot in timeslots for language in available_languages_per_slot[slot]):
            return False  # At least one student cannot find a suitable slot

    return True


def adjust_language_preferences(original_preferences, language_combination, timeslots):
    """
    Adjusts the language preferences based on a given language combination and timeslots.

    Args:
        original_preferences (dict): Original language preferences of students.
        language_combination (tuple): A tuple representing a combination of languages for the timeslots.
        timeslots (list): List of timeslots.

    Returns:
        dict: Adjusted language preferences.
    """
    adjusted_preferences = {}
    for student, preferences in original_preferences.items():
        adjusted_preferences[student] = {}
        for slot, language in zip(timeslots, language_combination):
            adjusted_preferences[student][slot] = preferences.get(language)
    return adjusted_preferences


def main():
    """
    Main function to find the optimal assignment of students to timeslots based on timeslot, language and group
    preferences.
    """
    start_time = time.time()
    logging.basicConfig(level=logging.CRITICAL)
    # Use the correct path to your JSON file
    # benchmark_file = os.path.join(os.path.expanduser('~'), 'Desktop', 'Bachelor Arbeit', 'Code', 'Projekt',
    # 'benchmarks', 'n50-s11-01')
    parser = (argparse.ArgumentParser(description='Solve the SmartAlloc problem.'))
    parser.add_argument('benchmark_file', type=str, help='Path to the benchmark file containing student and timeslot data.')
    args = parser.parse_args()
    benchmark_file = args.benchmark_file
    # Load data from the benchmark file
    students, timeslots, availability, num_students, language_preferences, group_preferences = (
        load_and_preprocess_data(benchmark_file))

    languages = ['E', 'G']  # Define the languages to consider
    best_solution_value = float('inf')
    best_combination = None
    best_assignment = []

    # Iterate over all possible language combinations
    for language_combination in itertools.product(languages, repeat=len(timeslots)):
        if not is_combination_feasible(language_preferences, language_combination, timeslots):
            # print(f"The problem is infeasible for {language_combination}")
            continue

        adjusted_language_preferences = adjust_language_preferences(language_preferences, language_combination,
                                                                    timeslots)
        solver = create_solver()
        if solver:
            x = define_variables(solver, students, timeslots)
            define_constraints(solver, x, students, timeslots, availability, num_students,
                               adjusted_language_preferences, group_preferences)
            define_objective(solver, x, students, timeslots, availability, adjusted_language_preferences)
            status = solver.Solve()

            if status == pywraplp.Solver.OPTIMAL:
                solution_value = solver.Objective().Value()
                if solution_value < best_solution_value:
                    best_solution_value = solution_value
                    best_combination = language_combination
                    best_assignment = [(student, slot) for student in students for slot in timeslots if
                                       x[student, slot].solution_value() == 1]
            elif status == pywraplp.Solver.INFEASIBLE:
                print(f"The problem is infeasible for {language_combination}.")
            else:
                print('The problem does not have an optimal solution.')

    # Output the number of students assigned to each timeslot

    # print(f'Best language combination: {best_combination}')
    # print('Optimal assignment:')
    # for student, slot in best_assignment:
        # print(f'Student {student} is assigned to the timeslot {slot}')

    # Output the number of students assigned to each timeslot

    # print('\nNumber of students per timeslot:')
    # for slot in timeslots:
        # num_students_assigned = sum(1 for student, assigned_slot in best_assignment if assigned_slot == slot)
        # print(f'Timeslot {slot}: {num_students_assigned} Student(en)')

    # print(best_solution_value)

    end_time = time.time()
    solve_time = end_time - start_time

    if best_solution_value != float('inf'):
        print(f"Total cost: {best_solution_value}")

    # print(f"Assignment: {best_assignment}") --
    if best_assignment:
        print(f"Assignment: {best_assignment}")

    print(f"Solve time: {solve_time}s")


if __name__ == "__main__":
    main()

