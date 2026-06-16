#!/usr/bin/env python3
"""
Génère un planning hebdomadaire CSV (créneaux de 15 min).
Script et CSV dans function-n-data/fast/.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

DAYS = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]
SLOTS_PER_DAY = 96
DAY_INDEX = {d: i for i, d in enumerate(DAYS)}

EXPECTED_QUARTERS = {
    "Sommeil": 60 * 4,
    "Prière": 6 * 4,
    "FI": 2 * 4,
    "Travail": int(57.5 * 4),
    "Cuisine": int(4.5 * 4),
    "Ménage": int(4.5 * 4),
    "Candidature": 5 * 4,
    "Eglise": 4 * 4,
    "Famille": 3 * 4,
    "Lessive": 1 * 4,
}


def generate_time_slots():
    return [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)]


def time_to_index(t):
    h, m = map(int, t.split(":"))
    return h * 4 + m // 15


def index_to_time(i):
    return f"{i // 4:02d}:{(i % 4) * 15:02d}"


def init_grid():
    return [["Libre"] * SLOTS_PER_DAY for _ in DAYS]


def apply_block(grid, day, start, end, activity):
    d = DAY_INDEX[day]
    s = time_to_index(start)
    e = time_to_index(end)
    if end == "23:45":
        e = SLOTS_PER_DAY
    for i in range(s, e):
        if grid[d][i] != "Libre":
            raise ValueError(f"Chevauchement {day} {index_to_time(i)} : "
                             f"{grid[d][i]} déjà placé, impossible d'ajouter {activity}")
        grid[d][i] = activity


def apply_cross_day_block(grid, start_day, start_time, end_day, end_time, activity):
    s = time_to_index(start_time)
    d1 = DAY_INDEX[start_day]
    for i in range(s, SLOTS_PER_DAY):
        if grid[d1][i] != "Libre":
            raise ValueError(f"Chevauchement {start_day} {index_to_time(i)} : "
                             f"{grid[d1][i]} déjà placé, impossible d'ajouter {activity}")
        grid[d1][i] = activity
    e = time_to_index(end_time)
    d2 = DAY_INDEX[end_day]
    for i in range(0, e):
        if grid[d2][i] != "Libre":
            raise ValueError(f"Chevauchement {end_day} {index_to_time(i)} : "
                             f"{grid[d2][i]} déjà placé, impossible d'ajouter {activity}")
        grid[d2][i] = activity


def build_planning():
    g = init_grid()

    # --- Sommeil (60h = 240 quarts) ---
    # Samedi→Dimanche : 12h (20:00→08:00)
    apply_cross_day_block(g, "samedi", "20:00", "dimanche", "08:00", "Sommeil")
    # Dimanche→Lundi : 8h (23:00→07:00)
    apply_cross_day_block(g, "dimanche", "23:00", "lundi", "07:00", "Sommeil")
    # 4 nuits normales 8h (19:15→03:15)
    for d in ("lundi", "mardi", "mercredi", "vendredi"):
        next_day = DAYS[(DAY_INDEX[d] + 1) % 7]
        apply_cross_day_block(g, d, "19:15", next_day, "03:15", "Sommeil")
    # Jeudi→Vendredi : 8h en 3 parties (contourne FI 19:30-21:30)
    apply_block(g, "jeudi", "16:00", "19:30", "Sommeil")
    apply_block(g, "jeudi", "21:30", "23:45", "Sommeil")
    apply_block(g, "vendredi", "00:00", "02:00", "Sommeil")

    # --- Prière (6h = 24 quarts) — pas le dimanche ---
    apply_block(g, "lundi", "07:00", "08:00", "Prière")
    apply_block(g, "mardi", "03:15", "04:15", "Prière")
    apply_block(g, "mercredi", "03:15", "04:15", "Prière")
    apply_block(g, "jeudi", "03:15", "04:15", "Prière")
    apply_block(g, "vendredi", "02:00", "03:00", "Prière")
    apply_block(g, "samedi", "03:15", "04:15", "Prière")

    # --- Travail (57h30 = 230 quarts) — mardi→samedi 04:15→15:45 ---
    for d in ("mardi", "mercredi", "jeudi", "vendredi", "samedi"):
        apply_block(g, d, "04:15", "15:45", "Travail")

    # --- Eglise (4h) dimanche 11:30→15:30 ---
    apply_block(g, "dimanche", "11:30", "15:30", "Eglise")

    # --- Famille (3h) dimanche 20:00→23:00 ---
    apply_block(g, "dimanche", "20:00", "23:00", "Famille")

    # --- FI (2h) jeudi 19:30→21:30 ---
    apply_block(g, "jeudi", "19:30", "21:30", "FI")

    # --- Cuisine (4h30 = 18 quarts) ---
    apply_block(g, "lundi", "12:00", "13:30", "Cuisine")
    apply_block(g, "mardi", "16:00", "17:30", "Cuisine")
    apply_block(g, "samedi", "16:00", "17:30", "Cuisine")

    # --- Ménage (4h30 = 18 quarts) ---
    apply_block(g, "mercredi", "16:00", "17:30", "Ménage")
    apply_block(g, "vendredi", "16:00", "17:30", "Ménage")
    apply_block(g, "dimanche", "15:30", "17:00", "Ménage")

    # --- Candidature (5h = 20 quarts) ---
    apply_block(g, "lundi", "10:00", "11:00", "Candidature")
    for d in ("mardi", "mercredi", "vendredi", "samedi"):
        apply_block(g, d, "17:30", "18:30", "Candidature")

    # --- Lessive (1h = 4 quarts) ---
    apply_block(g, "lundi", "14:00", "15:00", "Lessive")

    return g


def export_csv(grid, filepath):
    slots = generate_time_slots()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["horaire"] + DAYS)
        for i, t in enumerate(slots):
            w.writerow([t] + [grid[d][i] for d in range(len(DAYS))])


def check_volumes(grid):
    counter = Counter()
    for d in range(len(DAYS)):
        counter.update(grid[d])

    print("\n" + "=" * 65)
    print("  RÉCAPITULATIF DES VOLUMES")
    print("=" * 65)
    print(f"{'Activité':<15} {'Attendu':>10} {'Obtenu':>10} {'Statut':>10}")
    print("-" * 65)
    all_ok = True
    for act, exp_q in sorted(EXPECTED_QUARTERS.items()):
        got_q = counter.get(act, 0)
        ok_act = got_q == exp_q
        if not ok_act:
            all_ok = False
        print(f"{act:<15} {exp_q/4:>8.2f}h {got_q/4:>8.2f}h {'OK' if ok_act else 'ERREUR':>10}")
    libre_q = counter.get("Libre", 0)
    print(f"{'Libre':<15} {libre_q/4:>8.2f}h")
    print("-" * 65)
    total = sum(EXPECTED_QUARTERS.values()) + libre_q
    print(f"{'TOTAL':<15} {total/4:>8.2f}h")
    print("=" * 65)
    return all_ok, counter


def run_assertions(grid):
    for d in range(len(DAYS)):
        for s in range(SLOTS_PER_DAY):
            v = grid[d][s]
            assert v is not None and v != "", f"Cellule vide {DAYS[d]} {index_to_time(s)}"
    for d in range(len(DAYS)):
        assert len(grid[d]) == SLOTS_PER_DAY, f"{DAYS[d]}: {len(grid[d])} ≠ {SLOTS_PER_DAY}"
    counter = Counter()
    for d in range(len(DAYS)):
        counter.update(grid[d])
    for act, exp_q in EXPECTED_QUARTERS.items():
        assert counter.get(act, 0) == exp_q, f"{act}: {counter.get(act, 0)} ≠ {exp_q}"
    allowed = set(EXPECTED_QUARTERS) | {"Libre"}
    for d in range(len(DAYS)):
        for s in range(SLOTS_PER_DAY):
            assert grid[d][s] in allowed, f"Valeur inattendue '{grid[d][s]}'"
    print("✅ Toutes les assertions passent.")


def main():
    outdir = Path(__file__).parent
    outpath = outdir / "planning_hebdomadaire.csv"

    print("Génération du planning hebdomadaire...")
    grid = build_planning()
    export_csv(grid, outpath)
    print(f"CSV créé : {outpath}")

    all_ok, _ = check_volumes(grid)
    run_assertions(grid)

    if not all_ok:
        print("\n❌ Des volumes sont incorrects.")
        sys.exit(1)
    print("\n✅ Planning généré et validé avec succès.")


if __name__ == "__main__":
    main()
