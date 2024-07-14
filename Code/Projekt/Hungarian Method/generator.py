#!/usr/bin/env python3

import random
import json

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
TIMES = ["10:15-12:00", "12:15-14:00", "14:15-16:00", "16:15-18:00"]
EPSILON = 0.00001
LANGUAGE_PREF_ENCODED = {
  0: {"E" : 2, "G" : 0},
  1: {"E" : 2, "G" : 1},
  2: {"E" : 1, "G" : 2},
  3: {"E" : 2, "G" : 2}}


def generate(name, num_students, slot_weights, preteam_dist, language_pref, slot_pref):
    num_slots = len(slot_weights)
    team_size = len(preteam_dist)
    slots = []
    while (len(slots) < num_slots):
        slot = (random.choice(DAYS), random.choice(TIMES))
        if slot not in slots:
            slots.append(slot)

    assert sum(preteam_dist) - 1 < EPSILON, "the pre team distribution does not add up to 1"
    assert sum(language_pref) - 1 < EPSILON, "the language preference distribution does not add up to 1"
    assert len(slot_pref) == num_slots, "incosistent number of slots between slot weights and slot preferences"
    for slot in range(num_slots):
        assert len(slot_pref[slot]) == 3, f"slot #{slot} does not have 3 preferences"
        assert sum(slot_pref[slot]) - 1 < EPSILON, f"slot #{slot} preferences do not add up to 1"
      

    out = dict()
    out['team_size'] = team_size
    out['timeslots'] = dict()
    for s in range(num_slots):
        for i in range(slot_weights[s]):
            out['timeslots'][f"{slots[s][0][0:2]}{slots[s][1][0:2]}_{i}"] = f"{slots[s][0]} {slots[s][1]}"
    out['students'] = dict()

    students = ["S{:03d}".format(i+1) for i in range(num_students)]

    teams = []

    while len(students) > 0:
        rn_team = random.random()
        team_size = 0
        while rn_team > 0 and len(students) > team_size:
            team_size += 1
            rn_team -= preteam_dist[team_size-1]
        
        team = []
        for i in range(team_size):
            team.append(students.pop(random.randrange(len(students))))
        teams.append(team)

    for team in teams:
        rn_language = random.random()
        l_pref = -1
        while rn_language > 0:
            l_pref += 1
            rn_language -= language_pref[l_pref]
        
        slot_info = dict()
        for s in range(num_slots):
            rn_slot = random.random()
            s_pref = -1
            while rn_slot > 0:
                s_pref += 1
                rn_slot -= slot_pref[s][s_pref]
            for i in range(slot_weights[s]):
                slot_info[f"{slots[s][0][0:2]}{slots[s][1][0:2]}_{i}"] = s_pref
          
        for member in team:
            out['students'][member] = {
                "group": [m for m in team if m != member],
                "language": LANGUAGE_PREF_ENCODED[l_pref],
                "slot": slot_info
            }

    with open(name, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, sort_keys=True, indent=2)
        
#generate(name, num_students, slot_weights, preteam_dist, language_pref, slot_pref):

def main():
    generate("n50-s11-01", 50, [1,1], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7]])
    generate("n60-s11-01", 60, [1,1], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7]])
    generate("n70-s11-01", 70, [1,1], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7]])
    generate("n80-s11-01", 80, [1,2], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7]])
    generate("n90-s11-01", 90, [1,2], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7]])
    generate("n100-s11-01", 100, [1,2], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7]])
    generate("n110-s11-01", 110, [1,1,2], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7],[0.2,0.4,0.4]])
    generate("n120-s11-01", 120, [1,1,2], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7],[0.2,0.4,0.4]])
    generate("n130-s11-01", 130, [1,1,2], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7],[0.2,0.4,0.4]])
    generate("n140-s11-01", 140, [1,1,3], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7],[0.2,0.4,0.4]])
    generate("n150-s11-01", 150, [1,1,3], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7],[0.2,0.4,0.4]])
    generate("n160-s11-01", 160, [1,1,3], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7],[0.2,0.4,0.4]])
    generate("n170-s11-01", 170, [1,2,3], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7],[0.2,0.4,0.4]])
    generate("n180-s11-01", 180, [1,2,3], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7],[0.2,0.4,0.4]])
    generate("n190-s11-01", 190, [1,2,3], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7],[0.2,0.4,0.4]])
    generate("n200-s11-01", 200, [1,2,3], [0.75, 0.25], [0.05, 0.35, 0.35, 0.25], [[0.5, 0.2, 0.3],[0.1, 0.2, 0.7],[0.2,0.4,0.4]])
if __name__ == "__main__":
    main()
