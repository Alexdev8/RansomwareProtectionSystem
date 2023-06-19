import os
import time
import math
import requests
import hashlib
from collections import Counter

import PyPDF2
from PIL import Image
from docx import Document

# Chemin du dossier à surveiller
dossier = "."

# Spécifiez le chemin de la database
database = "database.txt"

# Your API key
API_KEY = os.environ.get('VIRUSTOTAL_API_KEY')

# Envoyer une alerte avec le message donné
def alerte(message):
    print(f"Alerte de sécurité : {message}. L'administrateur a été notifié.")

# Function to validate user inputs
def validate_user_input(user_input, valid_inputs):
    if user_input not in valid_inputs:
        raise ValueError(f"Invalid input {user_input}.")

# Initialiser la base de données des extensions de fichiers sensibles
def initialiser_base_de_donnees():
    # Vérifier si le fichier de la base de données existe
    if os.path.exists(database):
        # Si oui, ouvrir le fichier et lire les extensions de fichier
        with open(database, "r") as f:
            extensions = [line.lstrip(".") for line in f.read().splitlines()]
    else:
        # Sinon, afficher un message d'erreur
        print("La base de données n'existe pas.")
        extensions = []
    return extensions

# Charger tous les fichiers du système à partir du dossier spécifié
def charger_fichier_systeme(dossier):
    return [
        f
        for f in os.listdir(dossier)
        if os.path.isfile(os.path.join(dossier, f)) and f != database
    ]

# Vérifier si l'extension du fichier donné est dans la base de données
def verifier_extension(fichier, extensions):
    _, file_extension = os.path.splitext(fichier)
    file_extension = file_extension[1:]  
    return file_extension in extensions

# Vérifier si le fichier donné peut s'ouvrir
def verifier_ouverture_fichier(fichier):
    try:
        _, extension = os.path.splitext(fichier)
        if extension.lower() == '.docx':
            with open(fichier, 'r') as f:
                doc = Document(f)  # Essayer d'ouvrir le fichier comme un document Word
        elif extension.lower() == '.pdf':
            with open(fichier, 'rb') as f:
                reader = PyPDF2.PdfFileReader(f)  # Essayer d'ouvrir le fichier comme un PDF
        elif extension.lower() in ['.jpeg', '.jpg', '.png']:
            with open(fichier, 'rb') as f:
                img = Image.open(f)  # Essayer d'ouvrir le fichier comme une image JPEG
        #print(f"{fichier} peut être ouvert.")
        return False  # Si le fichier peut être ouvert, il n'est probablement pas chiffré
    except Exception as e:
        #print(f"{fichier} ne peut pas être ouvert. Il est possible qu'il soit chiffré.")
        return True  # Si le fichier ne peut pas être ouvert, il est possible qu'il soit chiffré

# Calculer l'entropie d'un fichier avec la formule de l'entropie de Shannon :   H(X) = -Σ [P(x) log2 P(x)]
def calc_entropie(fichier):
    with open(fichier, 'rb') as f:
        data = f.read()
    if not data:
        return 0
    entropie = 0
    frequence_donnee = Counter(data)
    len_data = len(data)
    for count in frequence_donnee.values():
        # Calculez la probabilité d'occurrence
        proba = count / len_data
        # Calculez l'entropie
        entropie += proba * math.log2(proba)
    return -entropie

# Analyser la réputation des fichiers
def get_file_hash(file_path):
    # Calculez le hash SHA-256 du fichier pour l'envoyer à VirusTotal
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def check_virustotal(file_id):
    url = f"https://www.virustotal.com/api/v3/files/{file_id}"

    headers = {
        "x-apikey": API_KEY, 
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à l'API de VirusTotal : {e}")
        return False

    if response.status_code == 200:
        json_response = response.json()
        # The file is known to VirusTotal
        if json_response['data']['attributes']['last_analysis_stats']['malicious'] > 0:
            return True  # The file is malicious
    return False  # The file is not known to VirusTotal or is not malicious

"""
def check_virustotal(file_id):
    url = f"https://www.virustotal.com/api/v3/files/{file_id}"

    headers = {
        "x-apikey": "8e596afede27939b50e366aaec39279d999bac72aa6f4a25b8c78a4a4f30ece9", 
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à l'API de VirusTotal : {e}")
        return False

    if response.status_code == 200:
        json_response = response.json()
        # The file is known to VirusTotal
        if json_response['data']['attributes']['last_analysis_stats']['malicious'] > 0:
            return True  # The file is malicious
    return False  # The file is not known to VirusTotal or is not malicious
"""

# Détection de comportements suspects
def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except OSError as e:
        return -1

def check_file_size(fichier, old_sizes, size_threshold):
    current_size = get_file_size(fichier)
    old_size = old_sizes.get(fichier, current_size)
    old_sizes[fichier] = current_size  # Toujours mettre à jour l'ancienne taille
    return abs(current_size - old_size) > size_threshold

# Surveiller en temps réel le système pour détecter toute activité suspecte
def surveiller(frequence, stop, extensions):
    compteur = 0
    old_sizes = {}
    size_threshold = 1000  # La taille de fichier doit changer de plus de 1000 octets = 1 ko pour déclencher une alerte

    while compteur < stop:
        print(f"\n-------- Etape de détection n°{compteur + 1} ----------------")
        try:
            fichiers_systeme = charger_fichier_systeme(dossier)  # Mettre à jour la liste des fichiers système à chaque itération
            for fichier in fichiers_systeme:
                fichier_path = os.path.join(dossier, fichier) 
                anomalie_detectee = False  # Aucune anomalie détectée au début

                # Verifier l extension
                if verifier_extension(fichier, extensions):
                    anomalie_detectee = True
                    alerte(f"Anomalie détectée : L'extension du fichier {fichier} figure dans la base de données de référence.")
                
                # Verifier si le fichier peut etre ouvert
                if not anomalie_detectee and verifier_ouverture_fichier(fichier_path):
                    anomalie_detectee = True
                    alerte(f"Anomalie détectée : Le fichier {fichier} ne peut pas être ouvert. Il est possible qu'il soit chiffré.")

                # Verifier l entropie du fichier
                if not anomalie_detectee:
                    entropie = calc_entropie(fichier_path) 
                    if entropie > 7:  # Déclencher une alerte si l'entropie est trop élevée
                        anomalie_detectee = True
                        alerte(f"Anomalie détectée : Le fichier {fichier} a une haute entropie ({entropie}). Il est possible qu'il soit chiffré.")

                # Verifier les changements significatifs de taille de fichier
                if not anomalie_detectee and check_file_size(fichier_path, old_sizes, size_threshold):
                    anomalie_detectee = True
                    alerte(f"Anomalie détectée : La taille du fichier {fichier} a changé de manière significative.")

                # Verifier la réputation du fichier
                if not anomalie_detectee:
                    file_hash = get_file_hash(fichier_path)
                    #print(f"Le hachage du fichier {fichier} est : {file_hash}")
                    if check_virustotal(file_hash):
                        anomalie_detectee = True
                        alerte(f"Anomalie détectée : Le fichier {fichier} est identifié comme malveillant par VirusTotal.")

                # Si aucune anomalie n'a été détectée pour ce fichier
                if not anomalie_detectee:
                    print(f"******* Le fichier {fichier} est sécurisé ********")

            time.sleep(frequence)

            compteur += 1

        except Exception as e:
            alerte(f"Erreur système : échec lors de l'accès au journal du système. Détails de l'erreur : {e}") 

# Analyser un seul fichier dans le système
def analyser_fichier(fichier_path, extensions):
    anomalie_detectee = False  # Aucune anomalie détectée au début
    
    # Verifier l extension
    if verifier_extension(fichier_path, extensions):
        anomalie_detectee = True
        alerte(f"Anomalie détectée : L'extension du fichier {os.path.basename(fichier_path)} figure dans la base de données de référence.")
                
    # Verifier si le fichier peut etre ouvert
    if not anomalie_detectee and verifier_ouverture_fichier(fichier_path):
        anomalie_detectee = True
        alerte(f"Anomalie détectée : Le fichier {os.path.basename(fichier_path)} ne peut pas être ouvert. Il est possible qu'il soit chiffré.")
    
    # Verifier l entropie du fichier
    if not anomalie_detectee:
        entropie = calc_entropie(fichier_path) 
        if entropie > 7:  # Déclencher une alerte si l'entropie est trop élevée
            anomalie_detectee = True
            alerte(f"Anomalie détectée : Le fichier {os.path.basename(fichier_path)} a une haute entropie ({entropie}). Il est possible qu'il soit chiffré.")
     
    # Verifier la réputation du fichier
    if not anomalie_detectee:
        file_hash = get_file_hash(fichier_path)
        if check_virustotal(file_hash):
            anomalie_detectee = True
            alerte(f"Anomalie détectée : Le fichier {os.path.basename(fichier_path)} est identifié comme malveillant par VirusTotal.")
    
    # Si aucune anomalie n'a été détectée pour ce fichier
    if not anomalie_detectee:
        print(f"******* Le fichier {os.path.basename(fichier_path)} est sécurisé ********")


# Test
# Test
def demander_choix(message, choix_valides):
    while True:
        choix = input(message).lower()
        if choix in choix_valides:
            return choix
        else:
            print(f"Choisissez une option valide parmi {', '.join(choix_valides)}")

try:
    # Initialiser la base de données
    extensions = initialiser_base_de_donnees()

    while True:  # Boucle infinie pour redemander en cas de mauvaise saisie
        mode = demander_choix("""Choisissez entre :
                               '1' pour une surveillance en temps réel
                               '2' pour analyser un seul fichier
                               '3' pour annuler et quitter le programme\n : """, ['1', '2', '3'])

        if mode == '1':
            while demander_choix("Voulez-vous continuer la surveillance (O/N) ? : ", ['o', 'n']) == 'o':
                try:
                    # Demander le nombre d'itérations et la fréquence
                    nb_iterations = int(input("Combien de fois voulez-vous surveiller le système ? : "))
                    frequence = int(input("Quelle doit être la fréquence (en secondes) de surveillance ? : "))
                except ValueError:
                    print("Veuillez entrer un nombre entier valide.")
                    continue
                # Démarrer la surveillance avec les paramètres spécifiés
                surveiller(frequence, nb_iterations, extensions)

            print("Surveillance arrêtée.")

        elif mode == '2':
            while demander_choix("Voulez-vous analyser un autre fichier (O/N) ? : ", ['o', 'n']) == 'o':
                # Afficher tous les fichiers dans le dossier
                fichiers_systeme = charger_fichier_systeme(dossier)
                print("Voici tous les fichiers dans le dossier spécifié :")
                for i, fichier in enumerate(fichiers_systeme, 1):
                    print(f"{i}. {fichier}")
                # Demander à l'utilisateur de choisir un fichier à analyser
                fichier_choisi = int(input("Entrez le numéro du fichier que vous souhaitez analyser : ")) - 1
                fichier_path = os.path.join(dossier, fichiers_systeme[fichier_choisi]) 
                # Analyser le fichier choisi
                analyser_fichier(fichier_path, extensions)

            print("Analyse arrêtée.")

        elif mode == '3':
            if demander_choix("Êtes-vous sûr de vouloir quitter (O/N) ? : ", ['o', 'n']) == 'o':
                print("Le programme a été annulé. Au revoir.")
                exit()
            else:
                print("Retour au choix des modes.")

        else:
            print("Le mode choisi n'est pas valide. Veuillez réessayer.")
    
except KeyboardInterrupt:
    print("\nInterruption du programme.")
