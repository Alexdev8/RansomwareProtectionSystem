import os
import signal
import sys
from datetime import datetime
from re import findall
from uuid import getnode

import numpy as np
import json
import requests
from dotenv import load_dotenv
from hashlib import sha256
from time import sleep, time

from docx import Document
from PyPDF2 import PdfFileReader
from PIL import Image
from cv2 import VideoCapture
from py_compile import compile

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from load_vars import get, get_keys
from prettytable import PrettyTable
from requests.exceptions import RequestException

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Utilitaires:
    def __init__(self, dossier: str, extensions: str, api_key: str):
        self.dossier = dossier
        self.extensions = extensions
        self.api_key = api_key

    # Afficher un message d'erreur personnalisé pour une meilleure traçabilité des erreurs
    @staticmethod
    def error_message(err_type: str, file_name: str, message: str) -> None:
        rel_file_path = os.path.relpath(file_name)
        print(f"{err_type} sur {rel_file_path}: {message}")

    # Envoyer une alerte avec le message donnéC
    def alerte(self, message: str) -> None:
        print(f"Alerte de sécurité : {message}. L'administrateur a été notifié.")
        
    # Charger tous les fichiers du système à partir du dossier spécifié
    @staticmethod
    def charger_fichier_systeme(dossier: str):
        try:
            chemin_dossier = os.path.abspath(dossier)
            return os.listdir(chemin_dossier)
        except FileNotFoundError:
            print(f"Le dossier {dossier} n'existe pas.")
            return []


    # Détection de comportements suspects
    # - Méthode pour obtenir la taille d'un fichier
    @staticmethod
    def get_file_size(file_path: str) -> int:
        try:
            return os.path.getsize(file_path)
        except OSError as e:
            return -1

    # - Méthode pour vérifier les changements significatifs de taille de fichier
    @staticmethod
    def check_file_size(file_path: str, old_sizes: dict, size_threshold: int) -> bool:
        current_size = Utilitaires.get_file_size(file_path)
        old_size = old_sizes.get(file_path, current_size)
        old_sizes[file_path] = current_size  # Mise à jour de l'ancienne taille
        return abs(current_size - old_size) > size_threshold

    # Méthode pour obtenir le hash SHA-256 d'un fichier
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        # Calculez le hash SHA-256 du fichier pour l'envoyer à VirusTotal
        hash_sha256 = sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except IOError as e:
            return None


class VerificationFichier:
    def __init__(self, file: str, api_key: str):
        self.file = file
        self.api_key = api_key

    # Vérifier si l'extension du fichier donné est dans la base de données
    def verifier_extension(self, extensions):
        _, file_extension = os.path.splitext(self.file)
        file_extension = file_extension[1:]
        return file_extension in extensions

    # Vérifier si le fichier donné peut s'ouvrir
    def verifier_ouverture_fichier(self) -> bool:
        extensions_connues = {
            'docx': Document,
            'pdf': PdfFileReader,
            'jpeg': Image.open,
            'jpg': Image.open,
            'png': Image.open,
            'txt': None,
            'csv': None,
            'xlsx': None,
            'pptx': None,
            'mp3': VideoCapture,
            'mp4': VideoCapture,
            'avi': VideoCapture,
            'gif': Image.open,
            'html': None,
            'xml': None,
            'json': json.load,
            'py': compile,
            'cpp': None,
            'java': None,
            'php': None,
            'c': None
        }
        
        _, extension = os.path.splitext(self.file)
        extension = extension[1:]

        if extension.lower() not in extensions_connues:
            return False

        verifier = extensions_connues[extension.lower()]

        if verifier is None:
            return True

        try:
            if extension.lower() in ['txt', 'csv', 'html', 'xml', 'c', 'cpp', 'java', 'php']:
                with open(self.file, 'r') as f:
                    f.read(1)
            else:
                verifier(self.file)
            return True
        except Exception:
            return False
    
    # Calculer l'entropie d'un fichier avec la formule de l'entropie de Shannon :   H(X) = -Σ [P(x) log2 P(x)]
    def calc_entropie(self) -> float:
        try:
            with open(self.file, 'rb') as f:
                data = np.frombuffer(f.read(), dtype=np.uint8)
            if not data.size:
                return 0
            counts = np.bincount(data)
            # Calculez la probabilité d'occurrence
            probabilities = counts / data.size
            # Remplacez les valeurs de probabilité nulles par un très petit nombre pour éviter la division par zéro
            probabilities[probabilities == 0] = 1e-10
            # Calculez l'entropie
            return -np.sum(probabilities * np.log2(probabilities))
        except Exception as e:
            #print(f"Erreur lors du calcul de l'entropie pour {self.file} : {e}")
            return None

    # Analyser la réputation des fichiers avec VirusTotal
    # - Méthode pour obtenir le hash du fichier
    def get_file_hash(self) -> str:
        return Utilitaires.get_file_hash(self.file)

    # - Vérifier la réputation du fichier en utilisant l'API de VirusTotal
    def check_virustotal(self) -> bool:
        file_id = self.get_file_hash(self.file)
        url = f"https://www.virustotal.com/api/v3/files/{file_id}"
        headers = {"x-apikey": self.api_key, "accept": "application/json"}

        try:
            response = requests.get(url, headers=headers, timeout=1000)
            response.raise_for_status() 
        except requests.exceptions.RequestException as e:
            #print(f"Erreur lors de l'appel à l'API de VirusTotal : {e}")
            return False

        if response.status_code == 200:
            json_response = response.json()
            return json_response['data']['attributes']['last_analysis_stats']['malicious'] > 0
        
        return False


class SurveillanceFichier(FileSystemEventHandler):
    def __init__(self, dossier, extensions, detection):
        super().__init__()
        self.dossier = dossier
        self.extensions = extensions
        self.detection = detection
        self.toutes_anomalies = []  # Initialiser toutes_anomalies

    def on_created(self, event):
        try:
            if not event.is_directory:
                fichier_path = event.src_path
                fichier_name = os.path.basename(fichier_path)
                if event.event_type == 'created':
                    print(f"Nouveau fichier créé : {fichier_name}")
                self.detection.analyser_fichier_unique(fichier_path, self.extensions)
        except Exception as e:
            self.detection.error_message("Erreur lors de la création du fichier", fichier_name, str(e))

    def on_modified(self, event):
        try:
            if not event.is_directory:
                fichier_path = event.src_path
                fichier_name = os.path.basename(fichier_path)
                print(f"Fichier modifié : {fichier_name}")
                self.detection.analyser_fichier_unique(fichier_path, self.extensions)
        except Exception as e:
            self.detection.error_message("Erreur lors de la modification du fichier", fichier_name, str(e))

    def on_deleted(self, event):
        try:
            if not event.is_directory:
                fichier_path = event.src_path
                fichier_name = os.path.basename(fichier_path)
                print(f"Fichier supprimé ou déplacé hors du répertoire surveillé: {fichier_name}")
        except Exception as e:
            self.detection.error_message("Erreur lors de la suppression du fichier", fichier_name, str(e))

    def on_moved(self, event):
        try:
            if not event.is_directory:
                fichier_path = event.src_path
                fichier_name = os.path.basename(fichier_path)
                dest_path_relative = os.path.relpath(
                    fichier_path, self.dossier)
                print(f"Fichier déplacé du répertoire surveillé vers : {dest_path_relative}")
                self.detection.analyser_fichier_unique(fichier_path, self.extensions)
        except Exception as e:
            self.detection.error_message("Erreur lors du déplacement du fichier", fichier_name, str(e))
    
    def on_any_event(self, event):
        try:
            if not event.is_directory:
                fichier_path = event.src_path
                fichier_name = os.path.basename(fichier_path)
                if event.event_type == 'created':
                    print(f"Nouveau fichier créé : {fichier_name}")
                elif event.event_type == 'modified':
                    print(f"Fichier modifié : {fichier_name}")
                elif event.event_type == 'deleted':
                    print(f"Fichier supprimé ou déplacé hors du répertoire surveillé: {fichier_name}")
                elif event.event_type == 'moved':
                    dest_path_relative = os.path.relpath(
                        fichier_path, self.dossier)
                    print(f"Fichier déplacé du répertoire surveillé vers : {dest_path_relative}")
                self.detection.analyser_fichier_unique(fichier_path, self.extensions)
        except Exception as e:
            self.detection.error_message("Erreur lors du traitement du fichier", fichier_name, str(e))

    def on_encrypted(self, file_path: str):
        try:
            size_threshold = 1000  # Taille de seuil en octets pour détecter une modification significative de la taille du fichier
            check_duration = 5  # Durée en secondes pendant laquelle vérifier le fichier
            check_interval = 1  # Intervalle en secondes entre chaque vérification

            start_time = time()
            size_changed = False

            while time() - start_time < check_duration:
                if self.detection.check_file_size(file_path, self.detection.old_sizes, size_threshold):
                    size_changed = True

                # Si l'entropie du fichier est élevée et que sa taille a changé, on peut supposer qu'il est en cours de chiffrement
                if size_changed and self.detection.calc_entropie(file_path) > 7:
                    fichier_name = os.path.basename(file_path)
                    self.detection.alerte(f"Le fichier {fichier_name} a été détecté comme chiffré.")

                sleep(check_interval)

        except Exception as e:
            fichier_name = os.path.basename(file_path)
            self.detection.error_message("Erreur lors de la vérification du fichier chiffré", fichier_name, str(e))

 
class RansomwareDetection(Utilitaires, VerificationFichier):
    def __init__(self, dossier: str, extensions: str, api_key: str):
        super().__init__(dossier, extensions, api_key)
        self.dossier = dossier
        self.extensions = extensions
        self.file = ""
        self.old_sizes = {}  # Suivre les changements de taille de fichier entre les appels à analyser_fichier_unique()
        self.fichiers_dangereux = 0  # Suivre le nombre de fichiers dangereux détectés
        self.toutes_anomalies = []  # Initialiser toutes_anomalies
        
    # Envoyez au serveur les anomalies de plusieurs fichiers
    def envoyer_anomalies_fichiers_au_serveur(self, anomalies):
        for anomalie in anomalies:
            # envoyer les anomalies au serveur
            token = os.getenv("ACCESS_TOKEN")
            headers = {"Authorization": f"Bearer {token}"}
            url = os.getenv("SERVER_ADDRESS") + '/' + get('VARS', 'CLIENT_ID') + '/machine/error'
            
            # Construction du message d'erreur
            error_data = {
                'type': anomalie['type'] if anomalie['type'] else 'PROBABLEMENT_SAIN',
                'file_path': anomalie['file_path'],
                'date': anomalie['date'].isoformat(),
                'message': anomalie['message']
            }
        
            params = {
                "machineAddress": ':'.join(['{:02x}'.format((getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1]),
            }

            json_data = json.dumps(error_data)
            response = requests.post(url, params=params, data=json_data, headers=headers)

            # Vérifier la réponse
            for _ in range(3):  # Effectuer jusqu'à 3 tentatives
                try:
                    if response.status_code == 201:
                        print(f"Anomalie pour {anomalie['file_path']} a été envoyée avec succès.")
                        break  # Sortir de la boucle en cas de succès
                    else:
                        print(f"Une erreur s'est produite pour {anomalie['file_path']}: {response.text}")
                except RequestException as e:
                    print(f"Erreur de connexion lors de l'envoi des anomalies : {str(e)}")
            else:
                print(f"Échec de l'envoi des anomalies pour {anomalie['file_path']} après plusieurs tentatives.")
    
    
    # Analyser un seul fichier dans le système
    def analyser_fichier_unique(self, file: str, extensions: list[str]) -> bool:
        try:
            file_name = os.path.basename(file)
            self.file = file  # Définir le fichier à analyser
            anomalies = []  # Liste pour stocker les anomalies détectées

            # obtenir la date et l'heure actuelle
            date = datetime.now()
            #date = maintenant.strftime('%d/%m/%Y, %H:%M:%S')
            
            # Vérifier l'extension
            if not self.verifier_extension(extensions):
                anomalies.append({
                    'type': 'EXTENSION',
                    'file_path': os.path.relpath(file),
                    'date': date,
                    'message': f"L'extension du fichier {file_name} ne figure pas dans la base de données de référence."
                })

            # Vérifier si le fichier peut être ouvert
            if not self.verifier_ouverture_fichier():
                anomalies.append({
                    'type': 'OUVERTURE',
                    'file_path': os.path.relpath(file),
                    'date': date,
                    'message': f"Le fichier {file_name} ne peut pas être ouvert. Il est possible qu'il soit chiffré."
                })

            # Vérifier l'entropie du fichier
            if not self.file:
                return False  # Ignorer si le fichier est vide
            entropie = self.calc_entropie()
            if entropie is not None and entropie > 7:
                anomalies.append({
                    'type': 'ENTROPIE',
                    'file_path': os.path.relpath(file),
                    'date': date,
                    'message': f"Le fichier {file_name} a une haute entropie ({entropie}). Il est possible qu'il soit chiffré."
                })

            # Vérifier les changements significatifs de taille de fichier
            # La taille de fichier doit changer de plus de 1000 octets = 1 ko pour déclencher une alerte
            size_threshold = 1000
            if Utilitaires.check_file_size(self.file, self.old_sizes, size_threshold):
                anomalies.append({
                    'type': 'TAILLE',
                    'file_path': os.path.relpath(file),
                    'date': date,
                    'message': f"La taille du fichier {file_name} a changé de manière significative."
                })

            # Vérifier la réputation du fichier
            if self.check_virustotal():
                anomalies.append({
                    'type': 'REPUTATION',
                    'file_path': os.path.relpath(file),
                    'date': date,
                    'message': f"Le fichier {file_name} est identifié comme malveillant par VirusTotal."
                })

            # Ajouter les anomalies détectées à toutes_anomalies
            self.toutes_anomalies.extend(anomalies)
            #print('Anomalies = ', anomalies)
            #print('Toutes anomalies =', self.toutes_anomalies)
            
            # Envoyer les anomalies au serveur
            self.envoyer_anomalies_fichiers_au_serveur(self.toutes_anomalies)

            ## ----------- BONUS ---------------##
            # construire le message d'anomalie
            msg_anomalie = "\n".join([anomalie['message'] for anomalie in anomalies]) or "Le fichier est probablement sécurisé."

            # créer une nouvelle table
            table = PrettyTable()
            table.field_names = ["Fichier", "Date", "Anomalies"]
            table.add_row([file_name, date, msg_anomalie])

            # afficher la table
            print(table)

            # ajouter au compteur de fichier potentiellement dangereux si une ou plusieurs anomalies
            if anomalies:
                self.fichiers_dangereux += 1

            return len(anomalies) > 0
        except Exception as e:
            self.alerte(f"Erreur lors de l'analyse du fichier {file}: {str(e)}")
            return False
        
    # Analyser les fichiers d'un dossier dans le système
    def analyser_fichiers_dossier(self, dossier: str) -> None:
        try:
            fichiers_systeme = Utilitaires.charger_fichier_systeme(dossier)
            dossier_absolu = os.path.abspath(dossier)
            for fichier in fichiers_systeme:
                fichier_path = os.path.join(dossier_absolu, fichier)
                if os.path.isfile(fichier_path):    # s'assurer que l'élément est un fichier et non un sous-dossier  
                    self.analyser_fichier_unique(fichier_path, self.extensions)
                # Envoyer les anomalies au serveur
                self.envoyer_anomalies_fichiers_au_serveur(self.toutes_anomalies)
        except Exception as e:
            self.alerte(f"Erreur lors de l'analyse des fichiers du dossier {dossier}: {str(e)}")

    # Analyser un dossier complet dans le système
    def analyser_dossier_complet(self, dossier: str) -> None:
        try:
            fichiers_systeme = Utilitaires.charger_fichier_systeme(dossier)
            for fichier in fichiers_systeme:
                fichier_path = os.path.join(dossier, fichier)
                fichier_rel_path = os.path.relpath(fichier_path, self.dossier)

                if os.path.isdir(fichier_path):
                    # Analyser le sous-dossier de manière récursive
                    self.analyser_dossier_complet(fichier_path)
                else:
                    print(f"Analyse du fichier : {fichier_rel_path}")
                    self.analyser_fichier_unique(fichier_path, self.extensions)
                # Envoyer les anomalies au serveur
                self.envoyer_anomalies_fichiers_au_serveur(self.toutes_anomalies)
        except Exception as e:
            self.alerte(f"Erreur lors de l'analyse du dossier {dossier}: {str(e)}")
    
     # Surveiller en temps réel le système pour détecter toute activité suspecte sans s'arrêter en cas de fichiers malveillants détectés
    def surveiller_no_arret(self, frequence, stop) -> None:
        compteur = 0
        while compteur < stop:
            print(f"\n-------- Étape de détection n°{compteur + 1} ----------------")
            self.fichiers_dangereux = 0  # réinitialiser le compteur à chaque itération
            try:
                # Analyser le dossier complet à chaque itération
                self.analyser_dossier_complet(self.dossier)
                print(f"Nombre de fichiers malveillants détectés : {self.fichiers_dangereux}")
                if self.fichiers_dangereux > 0:
                    self.alerte("Fichiers dangereux détectés.")
                
                # Envoyer les anomalies au serveur
                self.envoyer_anomalies_fichiers_au_serveur(self.toutes_anomalies)

                sleep(frequence)
                
            except Exception as e:
                self.alerte(f"Erreur système : échec lors de l'accès au journal du système. Détails de l'erreur : {e}")
            
            compteur += 1

    # Surveiller en temps réel le système pour détecter toute activité suspecte et s'arrêter en cas de fichiers malveillants détectés
    def surveiller_arret(self, frequence, stop, nb_max_fichiers_dangereux) -> None:
        compteur = 0
        while compteur < stop:
            print(f"\n-------- Étape de détection n°{compteur + 1} ----------------")
            self.fichiers_dangereux = 0  # réinitialiser le compteur à chaque itération
            try:
                # Analyser le dossier complet à chaque itération
                self.analyser_dossier_complet(self.dossier)

                # Vérifier si le nombre de fichiers dangereux atteint le seuil
                if self.fichiers_dangereux > nb_max_fichiers_dangereux:
                    print(f"Nombre de fichiers malveillants détectés : {self.fichiers_dangereux} > {nb_max_fichiers_dangereux}")
                else:
                    print(f"Nombre de fichiers malveillants détectés : {self.fichiers_dangereux} < {nb_max_fichiers_dangereux}")
                    
                if self.fichiers_dangereux >= nb_max_fichiers_dangereux:
                    print("Nombre maximal de fichiers dangereux atteint. Arrêt de l'analyse.")
                    break
                
                # Envoyer les anomalies au serveur
                self.envoyer_anomalies_fichiers_au_serveur(self.toutes_anomalies)

                sleep(frequence)

            except Exception as e:
                self.alerte(f"Erreur système : échec lors de l'accès au journal du système. Détails de l'erreur : {e}")
                
            compteur += 1

    # Surveiller les modifications du système de fichiers avec Watchdog
    def surveiller_watchdog(self, extensions):
        event_handler = SurveillanceFichier(self.dossier, extensions, self)
        observer = Observer()
        observer.schedule(event_handler, self.dossier, recursive=True)

        # Demander la durée de surveillance à l'utilisateur
        duree_surveillance = input("Entrez la durée de surveillance en secondes ou 'inf' pour une surveillance indéfinie : ")

        observer.start()
        try:
            if duree_surveillance.lower() == 'inf':
                while True:  # Boucle infinie qui se termine avec CTRL+C
                    sleep(1)
            else: 
                duree_surveillance = int(duree_surveillance)
                sleep(duree_surveillance)

        except KeyboardInterrupt:
            observer.stop()

        observer.stop()  # Arrêter l'observateur après la durée spécifiée
        observer.join()
        
        
        # Appeler on_encrypted pour chaque fichier après la surveillance
        fichiers_systeme = Utilitaires.charger_fichier_systeme(self.dossier)
        for fichier in fichiers_systeme:
            fichier_path = os.path.join(self.dossier, fichier)
            event_handler.on_encrypted(fichier_path)
            
        # Envoyer les anomalies au serveur
        self.envoyer_anomalies_fichiers_au_serveur(self.toutes_anomalies)


# Test
# Fonction de timeout
def timeout_handler(signum, frame):
    print("\nLe temps de réponse est écoulé. Arrêt du programme.")
    sys.exit()
    
def main():  
    signal.signal(signal.SIGALRM, timeout_handler)  # Configuration du signal de timeout

    def demander_choix(message: str, choix_valides: list[str]) -> str:
        signal.alarm(60)  # Délai de 60 secondes pour répondre à la demande de choix
        try:
            while True:
                choix = input(message).lower()
                if choix in choix_valides:
                    signal.alarm(0)  # Annuler le signal de timeout
                    return choix
                else:
                    print(f"Choisissez une option valide parmi {', '.join(choix_valides)}")
        except KeyboardInterrupt:
            print("\nInterruption du programme par l'utilisateur.")
            sys.exit()

    try:
        # Charger les variables d'environnement
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

        # Charger l'API VirusTotal du .env
        api_key = os.getenv("API_KEY_VIRUS_TOTAL")

        extensions = [get('FILES_EXTENSIONS', key) for key in get_keys('FILES_EXTENSIONS')]
        dossiers = [get('DOSSIERS', key) for key in get_keys('DOSSIERS')]
        
        utilitaires = {}
        detections = {}

        # Initialiser la base de données pour chaque dossier
        for dossier in dossiers:
            utilitaires[dossier] = Utilitaires(dossier, extensions, api_key)
            detections[dossier] = RansomwareDetection(dossier, extensions, api_key)

        while True:  # Boucle infinie pour redemander en cas de mauvaise saisie
            mode = demander_choix("""Choisissez le mode d'opération :
                                      \n\t'1' : Surveillance en temps réel sans arrêt (itérative)
                                      \n\t'2' : Surveillance en temps réel avec arrêt (itérative)
                                      \n\t'3' : Surveillance en temps réel avec Watchdog (événementielle)
                                      \n\t'4' : Analyser un fichier, les fichiers d'un dossier ou un dossier complet
                                      \n\t'5' : Quitter le programme
                                      \nVotre choix : """, ['1', '2', '3', '4', '5'])

            if mode in ['1', '2', '3', '4']:
                print("Veuillez choisir le dossier cible parmi les suivants :")
                for i, dossier in enumerate(dossiers, 1):
                    print(f"{i}. {dossier}")
                dossier_choisi = None
                while dossier_choisi is None:
                    try:
                        dossier_choisi = int(input("Entrez le numéro correspondant au dossier cible : ")) - 1
                        if dossier_choisi < 0 or dossier_choisi >= len(dossiers):
                            raise ValueError
                    except ValueError:
                        print("Veuillez entrer un numéro valide correspondant à un dossier.")
                        dossier_choisi = None
                dossier = dossiers[dossier_choisi]
                detection = detections[dossier]

            if mode == '1':
                while True:
                    if demander_choix("Voulez-vous commencer la surveillance ? (O/N) : ", ['o', 'n']) != 'o':
                        break
                    
                    # Demander le nombre de paramètres à définir
                    param_choice = int(input("Combien de paramètres voulez-vous définir (0, 1, 2) ? : "))
                    frequence = 10  # valeur par défaut
                    nb_iterations = float('inf')  # valeur par défaut
                    
                    # Demander la fréquence si nécessaire
                    if param_choice >= 1:
                        try:
                            frequence = int(input("Quelle doit être l'intervalle (en secondes) entre chaque cycle de surveillance ? : "))
                        except ValueError:
                            print("Veuillez entrer un nombre entier valide pour la fréquence.")

                    # Demander le nombre d'itérations si nécessaire
                    if param_choice == 2:
                        try:
                            nb_iterations = int(input("Combien de cycles de surveillance voulez-vous exécuter ? : "))
                        except ValueError:
                            print("Veuillez entrer un nombre entier valide pour le nombre d'itérations.")

                    detection.surveiller_no_arret(frequence, nb_iterations)
                    
                    # Envoyer les anomalies au serveur
                    if detection.toutes_anomalies:
                        detection.envoyer_anomalies_fichiers_au_serveur(detection.toutes_anomalies)
                        
                    if demander_choix("Voulez-vous continuer la surveillance ? (O/N) : ", ['o', 'n']) != 'o':
                        break

                print("Surveillance en temps réel sans arrêt arrêtée.")

            elif mode == '2':
                while True:
                    if demander_choix("Voulez-vous commencer la surveillance ? (O/N) : ", ['o', 'n']) != 'o':
                        break
                    
                    # Demander le nombre de paramètres à définir
                    param_choice = int(input("Combien de paramètres voulez-vous définir (0, 1, 2, 3) ? : "))
                    frequence = 10  # valeur par défaut
                    nb_iterations = float('inf')  # valeur par défaut
                    nb_max_fichiers_dangereux = 1  # valeur par défaut
                    
                    # Demander la fréquence si nécessaire
                    if param_choice >= 1:
                        try:
                            frequence = int(input("Quelle doit être l'intervalle (en secondes) entre chaque cycle de surveillance ? : "))
                        except ValueError:
                            print("Veuillez entrer un nombre entier valide pour la fréquence.")

                    # Demander le nombre d'itérations si nécessaire
                    if param_choice >= 2:
                        try:
                            nb_iterations = int(input("Combien de cycles de surveillance voulez-vous exécuter ? : "))
                        except ValueError:
                            print("Veuillez entrer un nombre entier valide pour le nombre d'itérations.")
        
                    # Demander le nombre maximal de fichiers dangereux si nécessaire
                    if param_choice == 3:
                        try:
                            nb_max_fichiers_dangereux = int(input("Combien de fichiers dangereux doivent être détectés pour arrêter la surveillance ? : "))
                        except ValueError:
                            print("Veuillez entrer un nombre entier valide pour le nombre maximal de fichiers dangereux.")

                    detection.surveiller_arret(frequence, nb_iterations, nb_max_fichiers_dangereux)
                    
                    # Envoyer les anomalies au serveur
                    if detection.toutes_anomalies:
                        detection.envoyer_anomalies_fichiers_au_serveur(detection.toutes_anomalies)
                        
                    if demander_choix("Voulez-vous continuer la surveillance ? (O/N) : ", ['o', 'n']) != 'o':
                            break
                        
                print("Surveillance en temps réel avec arrêt arrêtée.")

            elif mode == '3':
                while True:
                    if demander_choix("Voulez-vous commencer la surveillance ? (O/N) : ", ['o', 'n']) != 'o':
                        break
                    
                    # Démarrer la surveillance avec Watchdog
                    detection.surveiller_watchdog(extensions)
                    
                    if demander_choix("Voulez-vous continuer la surveillance ? (O/N) : ", ['o', 'n']) != 'o':
                            break
        
                print("Surveillance en temps réel avec Watchdog arrêtée.")

            elif mode == '4':
                while demander_choix("Voulez-vous commencer/continuer l'analyse d'un fichier, des fichiers d'un dossier ou d'un dossier complet ? (O/N) : ", ['o', 'n']) == 'o':
                    initial_dir = dossier
                    current_dir = dossier 
                    
                    while True:
                        print(f"Répertoire courant : {current_dir}")
                        print("Contenu du répertoire :")
                        dirs_files = os.listdir(current_dir)
                        for i, item in enumerate(dirs_files, 1):
                            print(f"\t{i}. {'(d)' if os.path.isdir(os.path.join(current_dir, item)) else '(f)'} {item}")
            
                        # si le répertoire courant est différent du répertoire initial, ajoutez l'option de retour
                        if current_dir != initial_dir:
                            print("\tR. Retourner au répertoire précédent")

                        action = input("Voulez-vous analyser le répertoire complet (C), seulement les fichiers du répertoire (F), un fichier spécifique (S), entrer dans un sous-répertoire (D), ou retourner au répertoire précédent (R) ? : ").lower()

                        if action == 'r': 
                            if current_dir != initial_dir:  # vérifie que l'utilisateur ne tente pas de remonter au-dessus du répertoire initial
                                    current_dir = os.path.dirname(current_dir)  # met à jour le répertoire courant à son parent
                            else:
                                print("Impossible de revenir au répertoire précédent depuis le répertoire initial.")
                        elif action == 'c':
                            detection.analyser_dossier_complet(current_dir)
                            break
                        elif action == 'f':
                            detection.analyser_fichiers_dossier(current_dir)
                            break
                        elif action == 's':
                            file_num = int(input("Entrez le numéro du fichier que vous voulez analyser : ")) - 1
                            if file_num < 0 or file_num >= len(dirs_files) or os.path.isdir(os.path.join(current_dir, dirs_files[file_num])):
                                print("Numéro de fichier invalide.")
                            else:
                                detection.analyser_fichier_unique(os.path.join(current_dir, dirs_files[file_num]), extensions)
                                break
                        elif action == 'd':
                            dir_num = int(input("Entrez le numéro du sous-répertoire que vous voulez entrer : ")) - 1
                            if dir_num < 0 or dir_num >= len(dirs_files) or not os.path.isdir(os.path.join(current_dir, dirs_files[dir_num])):
                                print("Numéro de répertoire invalide.")
                            else:
                                current_dir = os.path.join(current_dir, dirs_files[dir_num])
                        else:
                            print("Choix non valide.")
                            
                    print("Analyse de fichier/dossier terminée.")

            elif mode == '5':
                if demander_choix("Êtes-vous sûr de vouloir quitter le programme ? (O/N) : ", ['o', 'n']) == 'o':
                    print("Vous avez choisi de quitter le programme. Au revoir.")
                    exit()
                else:
                    print("Retour au menu de sélection du mode d'opération.")

            else:
                print("Le mode choisi n'est pas reconnu. Veuillez réessayer.")

    except KeyboardInterrupt:
        print("\nInterruption du programme par l'utilisateur.")

if __name__ == "__main__":
    main()