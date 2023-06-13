import os
import time

# Spécifiez le chemin de la database 
database = "database.txt"

# Chemin du dossier
dossier = "."

def initialiser_base_de_donnees():
    if os.path.exists(database):
        with open(database, "r") as f:
            extensions = [line.lstrip(".") for line in f.read().splitlines()]
    else:
        print("La base de données n'existe pas.")
        extensions = []

    return extensions

def charger_fichier_systeme(dossier):
    return [
        f
        for f in os.listdir(dossier)
        if os.path.isfile(os.path.join(dossier, f)) and f != database
    ]

def verifier_extension(fichier, extensions):
    _, file_extension = os.path.splitext(fichier)
    file_extension = file_extension[1:]  
    return file_extension in extensions

def alerte(message):
    # Insérez ici le code pour envoyer une notification
    print(f"Alerte : {message}. Administrateur a été notifié.")

def surveiller(frequence, stop, extensions):
    compteur = 0
    while compteur < stop:
        try:
            fichiers_systeme = charger_fichier_systeme(dossier)
            for fichier in fichiers_systeme:
                if resultat_extension := verifier_extension(
                    fichier, extensions
                ):
                    alerte(f"Attaque détectée : L'extension du fichier {fichier} est dans la base de données.")
                else:
                    print(f"Etat du système : Sain. L'extension du fichier {fichier} n'est pas dans la base de données.")
            time.sleep(frequence)
            compteur += 1
        except Exception as e:
            print(f"Erreur lors du chargement du journal du système: {e}")
            alerte(f"Erreur lors du chargement du journal du système: {e}")

extensions = initialiser_base_de_donnees()
surveiller(5, 2, extensions)  # Démarrer la surveillance toutes les 5 secondes pour 2 itérations
