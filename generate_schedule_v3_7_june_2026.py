import csv
import os

# Configuration
days = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
time_slots = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)]

# Initialiser la grille avec "Libre"
schedule = {day: ["Libre"] * 96 for day in days}

def fill_activity(day, start_h, start_m, duration_min, activity):
    """Remplit les créneaux de 15 min correspondant à l'activité"""
    start_idx = start_h * 4 + start_m // 15
    slots = (duration_min + 14) // 15  # arrondi en excès
    for i in range(slots):
        if start_idx + i < 96:
            schedule[day][start_idx + i] = activity

# --- SOMMEIL ---
# Dimanche : 12h (00h-08h + 20h-23h45)
fill_activity("Dimanche", 0, 0, 8*60, "Sommeil")
fill_activity("Dimanche", 20, 0, 4*60, "Sommeil")
# Lundi à Samedi : 8h (00h-08h)
for d in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]:
    fill_activity(d, 0, 0, 8*60, "Sommeil")

# --- PRIÈRE ---
# 6 jours x 1h. 5 jours avant travail (3h30-4h30), + Dimanche matin (8h-9h)
for d in ["Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]:
    fill_activity(d, 3, 30, 60, "Prière")
fill_activity("Dimanche", 8, 0, 60, "Prière")

# --- FI ---
# 2h x 1 jour (Lundi 9h-11h)
fill_activity("Lundi", 9, 0, 2*60, "FI")

# --- TRAVAIL ---
# Mardi à Samedi, 4h30-15h37 (11h7min x 5 jours)
for d in ["Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]:
    fill_activity(d, 4, 30, 11*60 + 7, "Travail")

# --- CUISINE ---
# 1h30 x 3 jours (Lundi 11h-12h30, Mardi 16h-17h30, Mercredi 16h-17h30)
fill_activity("Lundi", 11, 0, 90, "Cuisine")
fill_activity("Mardi", 16, 0, 90, "Cuisine")
fill_activity("Mercredi", 16, 0, 90, "Cuisine")

# --- MÉNAGE ---
# 1h30 x 3 jours (Jeudi 16h-17h30, Vendredi 16h-17h30, Dimanche 16h-17h30)
fill_activity("Jeudi", 16, 0, 90, "Ménage")
fill_activity("Vendredi", 16, 0, 90, "Ménage")
fill_activity("Dimanche", 16, 0, 90, "Ménage")

# --- CANDIDATURE ---
# 1h x 5 jours (Lundi 12h30-13h30, Mardi-Jeudi 17h30-18h30)
fill_activity("Lundi", 12, 30, 60, "Candidature")
for d in ["Mardi", "Mercredi", "Jeudi", "Vendredi"]:
    fill_activity(d, 17, 30, 60, "Candidature")

# --- ÉGLISE ---
# Dimanche 11h30-15h30 (4h)
fill_activity("Dimanche", 11, 30, 4*60, "Eglise")

# --- FAMILLE ---
# Samedi 20h-23h (3h)
fill_activity("Samedi", 20, 0, 3*60, "Famille")

# --- LESSIVE ---
# Dimanche 10h-11h (1h)
fill_activity("Dimanche", 10, 0, 60, "Lessive")

# Écriture du CSV
output_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "planning_hebdomadaire.csv")

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # En-tête
    writer.writerow(["Heure"] + days)
    # Données
    for i, t in enumerate(time_slots):
        row = [t] + [schedule[d][i] for d in days]
        writer.writerow(row)

print(f"✅ CSV généré : {output_path}")

# Vérification des volumes
print("\n📊 Volumes horaires par activité :")
from collections import Counter
for activity in ["Sommeil", "Prière", "FI", "Travail", "Cuisine", "Ménage", "Candidature", "Eglise", "Famille", "Lessive", "Libre"]:
    total_min = sum(sum(1 for slot in schedule[d] if slot == activity) * 15 for d in days)
    total_h = total_min // 60
    total_m = total_min % 60
    print(f"  {activity} : {total_h}h{total_m:02d}")
