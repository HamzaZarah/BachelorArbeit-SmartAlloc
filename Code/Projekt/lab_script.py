#! /usr/bin/env python

"""
This script sets up and runs an experiment using the SmartAlloc and Hungarian Method solvers
to solve assignment problems. It is designed to work both in local and remote environments,
specifically targeting the Basel Slurm Environment for remote execution. The experiment
involves running specified algorithms on a set of benchmark problems, parsing the output,
and generating a report of the results.
"""

import glob
import os
import platform


from downward.reports.absolute import AbsoluteReport
from lab.environments import BaselSlurmEnvironment, LocalEnvironment
from lab.experiment import Experiment
from lab.parser import Parser
from lab.reports import Attribute


# Custom report class to include specific information and error attributes in the report.
class BaseReport(AbsoluteReport):
    INFO_ATTRIBUTES = ["time_limit", "memory_limit", "seed"]  # Attributes to be included in the report's info section.
    ERROR_ATTRIBUTES = [
        "domain",  # Domain of the problem consisting of students?
        "problem",  # The problem consisting of students and time slots?
        "algorithm",  # The mixed-integer linear programming algorithm and the Hungarian method.
        "unexplained_errors",  # Unexplained errors that occurred during the experiment.
        "error",  # Error status of the run.
        "node",  # Node where the run was executed.
    ]  # Attributes to be included in the report's error section.


# Determine the execution environment (local or remote) based on the node name.
NODE = platform.node()
REMOTE = NODE.endswith(".scicore.unibas.ch") or NODE.endswith(".cluster.bc2.ch")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of the script.
BENCHMARKS_DIR = os.path.join(SCRIPT_DIR, "benchmarks")  # Directory containing benchmark files.
BENCHMARKS = sorted(glob.glob(os.path.join(BENCHMARKS_DIR, "*.json")))  # List of benchmark files.
ALGORITHMS = ["smartalloc", "hungarian"]  # Algorithms to be used in the experiment.
SEED = 2023  # Seed for random number generation.
TIME_LIMIT = 1800  # Time limit for each run in seconds.
MEMORY_LIMIT = 4000  # Memory limit for each run in megabytes.

# Configure the environment based on whether the script is running remotely.
if REMOTE:
    ENV = BaselSlurmEnvironment(email="h.zarah@stud.unibas.ch")  # Remote environment configuration.
    SUITE = BENCHMARKS  # Use all benchmarks for remote execution.
else:
    ENV = LocalEnvironment(processes=2)  # Local environment configuration.
    SUITE = BENCHMARKS[:2]  # Use a subset of benchmarks for local testing.

# Attributes to be collected and reported for each run.
ATTRIBUTES = [
    "assignment",  # Assignment of students to time slots.
    "total_cost",  # Total cost of the assignment.
    "error",
    "solve_time",
    "solver_exit_code",  # Exit code of the solver.
    Attribute("solved", absolute=True),  # Boolean indicating whether the problem was solved.
]


def make_parser():
    """
    Creates a parser for extracting information from solver output.

    This function sets up a parser that scans through the solver's output logs to extract
    essential information such as the node, solver exit code, assignment details, total cost,
    and solve time. It also assesses whether the problem was solved successfully and identifies
    any errors that occurred during the process. The parser uses regular expressions to find
    specific patterns in the text that match the expected output format of the solver.

    Returns:
        Parser: A configured parser object for extracting run information.
    """
    def solved(content, props):
        """
        Determines if the problem was solved based on the presence of an assignment in the properties.

        This function checks if the 'assignment' key exists in the properties dictionary, indicating
        that an assignment was found and thus the problem was considered solved. It updates the
        'solved' key in the properties dictionary with a boolean value representing the outcome.

        Args:
            content (str): The content of the output log (unused in this function).
            props (dict): The properties dictionary where the 'solved' status is updated.
        """
        props["solved"] = int("assignment" in props)  # Determine if the problem was solved.

    def error(content, props):
        """
        Identifies and sets the error status based on whether the problem was solved.

        This function updates the 'error' key in the properties dictionary with a string
        indicating the error status. If the problem was solved, it sets the error status to
        'assignment-found'. Otherwise, it marks the problem as 'unsolved'.

        Args:
            content (str): The content of the output log (unused in this function).
            props (dict): The properties dictionary where the error status is updated.
        """
        if props["solved"]:
            props["error"] = "assignment-found"
        else:
            props["error"] = "unsolved"

    vc_parser = Parser()
    vc_parser.add_pattern("node", r"node: (.+)\n", type=str, file="driver.log", required=True)
    vc_parser.add_pattern("solver_exit_code", r"solve exit code: (.+)\n", type=int, file="driver.log")
    vc_parser.add_pattern("assignment", r"Assignment: (\[.*\])", type=str)
    vc_parser.add_pattern("total_cost", r"Total cost: (.+)\n", type=float)
    vc_parser.add_pattern("solve_time", r"Solve time: (.+)s", type=float)
    vc_parser.add_function(solved)
    vc_parser.add_function(error)
    return vc_parser


# Create a new experiment.
exp = Experiment(environment=ENV)
# Add solver to experiment and make it available to all runs.
exp.add_resource("solver_smartalloc", os.path.join(SCRIPT_DIR, "SmartAlloc/solver.py"))
exp.add_resource("solver_hungarian", os.path.join(SCRIPT_DIR, "Hungarian Method/hungarian_method.py"))
# Add custom parser.
exp.add_parser(make_parser())

for algo in ALGORITHMS:
    for task in SUITE:
        run = exp.add_run()
        run.add_resource("task", task, symlink=True)
        solver_file = "solver_smartalloc" if algo == "solver.py" else "solver_hungarian"
        run.add_command(
            "solve",
            ["{" + solver_file + "}", "--seed", str(SEED), "{task}"],
            time_limit=TIME_LIMIT,
            memory_limit=MEMORY_LIMIT,
        )
        domain = os.path.basename(os.path.dirname(task))
        task_name = os.path.basename(task)
        run.set_property("domain", domain)
        run.set_property("problem", task_name)
        run.set_property("algorithm", algo)
        run.set_property("time_limit", TIME_LIMIT)
        run.set_property("memory_limit", MEMORY_LIMIT)
        run.set_property("seed", SEED)
        run.set_property("id", [algo, domain, task_name])

# Add step that writes experiment files to disk.
exp.add_step("build", exp.build)

# Add step that executes all runs.
exp.add_step("start", exp.start_runs)

# Add step that parses the logs.
exp.add_step("parse", exp.parse)

# Add step that collects properties from run directories and writes them to *-eval/properties.
exp.add_fetcher(name="fetch")

# Make a report.
exp.add_report(BaseReport(attributes=ATTRIBUTES), outfile="report.html")

# Parse the commandline and run the given steps.
exp.run_steps()


