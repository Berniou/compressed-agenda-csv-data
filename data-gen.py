import pandas as pd
from datetime import datetime, timedelta

jours = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]

# Créneaux de 00h00 à 23h45 par pas de 15 minutes
heures = []
depart = datetime(2000, 1, 1, 0, 0)
for i in range(96):
    t = depart + timedelta(minutes=15 * i)
    heures.append(t.strftime("%Hh%M"))

# Exemple d'organisation des activités
planning = []

for heure in heures:
    row = {"heure": heure}

    if heure < "06h00":
        activite = "Sommeil"
    elif heure < "09h00":
        activite = "Prière" if heure < "08h00" else "Sommeil"
    elif heure < "15h00":
        activite = "Travail"
    elif heure < "19h00":
        activite = "Travail" if heure < "18h00" else "Candidature"
    else:
        activite = "Cuisine"

    for jour in jours:
        row[jour] = activite

    planning.append(row)

df = pd.DataFrame(planning, columns=["heure"] + jours)

# Sauvegarde CSV avec encodage compatible Excel
df.to_csv("data/planning_hebdo.csv", index=False, encoding="utf-8-sig")

print(df.head())