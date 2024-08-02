#!/usr/bin/env python3

import math
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
        

def get_slots(num_students):
    num_slots = math.ceil(num_students / 60)
    slots = [1,1]
    for i in range(2,num_slots):
        rn_new_slot = random.randint(0, len(slots))
        if rn_new_slot == len(slots):
            slots.append(1)
        else:
            slots[rn_new_slot] += 1
    return slots

# pref types:
# 0: all slots have the same "normal" distribution
# 1: one slot is preferred, one disliked, rest normal
# 2: one slot is extremely preferred, one extremely disliked, rest normal
prefs = {
  "p+": [0.05, 0.15, 0.8],
  "p" : [0.1, 0.3, 0.6],
  "n" : [0.3, 0.4, 0.3],
  "d" : [0.6, 0.3, 0.1],
  "d+": [0.8, 0.15, 0.05]
}
def get_slot_prefs(num_slots, pref_type):
    slot_prefs = [prefs["n"]]*num_slots
    if pref_type == 1:
        slot_prefs[0] = prefs["p"]
        slot_prefs[1] = prefs["d"]
    elif pref_type == 2:
        slot_prefs[0] = prefs["p+"]
        slot_prefs[1] = prefs["d+"]
    random.shuffle(slot_prefs)
    return slot_prefs
          
def main():
    for n in [50, 60, 70, 80, 90, 100, 125, 150, 175, 200, 300, 400, 500, 750, 1000, 1500, 2000]:
        for pref_type in [0,1,2]:
            for i in range(10):
                slots = get_slots(n)
                slot_prefs = get_slot_prefs(len(slots), pref_type)
                generate(f"n{n}-p{pref_type}-{i}",
                         n, slots, [0.75, 0.25], [0.05, 0.35, 0.35, 0.25],
                         slot_prefs)

if __name__ == "__main__":
    main()
