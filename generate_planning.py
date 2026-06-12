import pandas as pd
import os

# Dossier de sortie
os.makedirs("data", exist_ok=True)

jours = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]

# Créneaux de 00h00 à 23h45 par pas de 15 minutes
creneaux = []
for h in range(24):
    for m in (0, 15, 30, 45):
        creneaux.append(f"{h:02d}h{m:02d}")

def get_activite(jour, heure_str):
    """Retourne l'activité pour un jour et un créneau donné."""
    h = int(heure_str[:2])
    m = int(heure_str[3:])
    minute = h * 60 + m

    # Dimanche : repos, église, famille, lessive
    if jour == "dimanche":
        if (0 <= minute < 540) or (1260 <= minute < 1440):
            return "Sommeil"          # 00h-09h + 21h-00h = 12h
        elif 540 <= minute < 600:
            return "Libre"            # 09h-10h
        elif 600 <= minute < 840:
            return "Eglise"           # 10h-14h = 4h
        elif 840 <= minute < 1020:
            return "Famille"          # 14h-17h = 3h
        elif 1020 <= minute < 1110:
            return "Cuisine"          # 17h-18h30
        elif 1110 <= minute < 1200:
            return "Ménage"           # 18h30-20h
        elif 1200 <= minute < 1260:
            return "Lessive"          # 20h-21h = 1h
        else:
            return "Libre"

    # Lundi à Vendredi : travail arrondi par excès (11h15) + candidature + activité
    elif jour in ("lundi", "mardi", "mercredi", "jeudi", "vendredi"):
        if (0 <= minute < 420) or (1380 <= minute < 1440):
            return "Sommeil"          # 00h-07h + 23h-00h = 8h
        elif 420 <= minute < 480:
            return "Prière"           # 07h-08h = 1h
        elif 480 <= minute < 540:
            return "Libre"            # 08h-09h
        elif 540 <= minute < 1215:
            return "Travail"          # 09h-20h15 = 11h15 (arrondi par excès de ~11h02)
        elif 1215 <= minute < 1275:
            return "Candidature"      # 20h15-21h15 = 1h
        elif 1275 <= minute < 1365:
            # Cuisine lundi/mercredi/vendredi, Ménage mardi/jeudi
            if jour in ("lundi", "mercredi", "vendredi"):
                return "Cuisine"      # 21h15-22h45 = 1h30
            else:
                return "Ménage"       # 21h15-22h45 = 1h30
        elif 1365 <= minute < 1380:
            return "Libre"            # 22h45-23h
        else:
            return "Libre"

    # Samedi : repos, FI, ménage
    elif jour == "samedi":
        if 0 <= minute < 480:
            return "Sommeil"          # 00h-08h = 8h
        elif 480 <= minute < 600:
            return "FI"               # 08h-10h = 2h
        elif 600 <= minute < 1260:
            return "Libre"            # 10h-21h
        elif 1260 <= minute < 1350:
            return "Ménage"           # 21h-22h30 = 1h30
        elif 1350 <= minute < 1440:
            return "Libre"            # 22h30-00h
        else:
            return "Libre"

    return "Libre"

# Construction du DataFrame
rows = []
for heure in creneaux:
    row = {"heure": heure}
    for jour in jours:
        row[jour] = get_activite(jour, heure)
    rows.append(row)

df = pd.DataFrame(rows, columns=["heure"] + jours)

# Sauvegarde CSV dans le dossier data/
df.to_csv("data/planning_hebdo.csv", index=False, encoding="utf-8-sig")

# Affichage des 20 premières lignes
print("=== Aperçu des 20 premières lignes ===")
print(df.head(20).to_string(index=False))

# Vérification des volumes hebdomadaires
print("\n=== Vérification des volumes hebdomadaires (en heures) ===")
for jour in jours:
    total_creneaux = df[jour].count()  # tous les créneaux
    for activite in df[jour].unique():
        if activite == "Libre":
            continue
        nb = (df[jour] == activite).sum()
        heures = nb * 15 / 60
        if heures > 0:
            print(f"{jour:10s} | {activite:12s} | {heures:.2f}h")
