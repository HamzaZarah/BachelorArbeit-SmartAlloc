import json

# Load properties.json
with open('/Users/hamzazarah/Desktop/Bachelor Arbeit/Code/Projekt/properties.json') as f:
    data = json.load(f)

# Initialize structures to store solving times by preference type
results = {'p0': {}, 'p1': {}, 'p2': {}}

# Iterate over all problem instances in the JSON
for key, value in data.items():
    problem_id = value['id']  # Extract problem ID

    # Handle the case where problem_id might be a list
    if isinstance(problem_id, list):
        problem_id = '-'.join(problem_id)

    # Now problem_id should be a string like "smartalloc_without_group_preference-benchmarks-n90-p0-1"
    try:
        # Split the problem_id based on dashes and locate n, p values
        parts = problem_id.split('-')

        # Find the parts that contain 'n' and 'p'
        n_part = next(part for part in parts if part.startswith('n'))
        p_part = next(part for part in parts if part.startswith('p'))

        n = int(n_part[1:])  # Extract the number of students, e.g., 'n90' -> 90
        p = p_part  # Use the full 'p0', 'p1', or 'p2'

    except (IndexError, ValueError, StopIteration) as e:
        print(f"Error parsing problem_id: {problem_id}")
        continue  # Skip this entry if there's an issue

    # Ensure we're only working with valid preference types
    if p in results:
        if (n, p) not in results[p]:
            results[p][(n, p)] = {}

        # Add algorithm results if solved
        algorithm = value['algorithm']
        if value['solved'] == 1:
            if algorithm not in results[p][(n, p)]:
                results[p][(n, p)][algorithm] = []
            results[p][(n, p)][algorithm].append(value['solve_time'])

# Filter out instances where not all algorithms have results and generate coordinates
max_time = 10000  # A large constant to represent failed cases
coordinates = {'p0': [], 'p1': [], 'p2': []}

for pref_key, pref_results in results.items():
    for (n, p), alg_results in pref_results.items():
        if all(alg in alg_results for alg in ['hungarian', 'smartalloc', 'smartalloc_without_group_preference']):
            for i in range(len(alg_results['hungarian'])):
                x_hungarian = alg_results['hungarian'][i]
                y_smartalloc = alg_results['smartalloc'][i] if i < len(alg_results['smartalloc']) else max_time
                y_smartalloc_no_pref = alg_results['smartalloc_without_group_preference'][i] if i < len(
                    alg_results['smartalloc_without_group_preference']) else max_time

                coordinates[pref_key].append({
                    'smartalloc': (x_hungarian, y_smartalloc),
                    'smartalloc_no_pref': (x_hungarian, y_smartalloc_no_pref)
                })

# Output the coordinates by preference type
for pref_key in ['p0', 'p1', 'p2']:
    print(f"\nHungarian vs SmartAlloc for {pref_key}:")
    for coord in coordinates[pref_key]:
        print(coord['smartalloc'])

    print(f"\nHungarian vs SmartAlloc without Group Preference for {pref_key}:")
    for coord in coordinates[pref_key]:
        print(coord['smartalloc_no_pref'])
