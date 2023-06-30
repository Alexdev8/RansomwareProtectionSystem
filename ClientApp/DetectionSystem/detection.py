import os
import sys
from datetime import datetime
from uuid import getnode

import numpy as np
import json
import requests
from dotenv import load_dotenv
from hashlib import sha256

from PyPDF2 import PdfFileReader
from PIL import Image
from cv2 import VideoCapture
from py_compile import compile
from time import sleep

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ClientApp.load_vars import get, get_keys
from requests.exceptions import RequestException

nb_anomalies = 0
class Utilitaires:
    def __init__(self, dossier: str, extensions: str, api_key: str):
        self.dossier = dossier
        self.extensions = extensions
        self.api_key = api_key

    # Afficher un message d'erreur personnalisé pour une meilleure traçabilité des erreurs
    @staticmethod
    def error_message(err_type: str, file_name: str, message: str) -> None:
        rel_file_path = os.path.abspath(file_name)
        print(f"{err_type} sur {rel_file_path}: {message}")

    # Envoyer une alerte avec le message donnéC
    def alerte(self, message: str) -> None:
        print(
            f"Alerte de sécurité : {message}. L'administrateur a été notifié.")

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
            'docx': None,
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
            if extension.lower() in ['docx', 'txt', 'csv', 'html', 'xml', 'c', 'cpp', 'java', 'php']:
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
            # print(f"Erreur lors du calcul de l'entropie pour {self.file} : {e}")
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
            # print(f"Erreur lors de l'appel à l'API de VirusTotal : {e}")
            return False

        if response.status_code == 200:
            json_response = response.json()
            return json_response['data']['attributes']['last_analysis_stats']['malicious'] > 0

        return False


class RansomwareDetection(Utilitaires, VerificationFichier):
    def __init__(self, dossier: str, extensions: str, api_key: str):
        super().__init__(dossier, extensions, api_key)
        self.dossier = dossier
        self.extensions = extensions
        self.file = ""
        # Suivre les changements de taille de fichier entre les appels à analyser_fichier_unique()
        self.old_sizes = {}
        self.fichiers_dangereux = 0  # Suivre le nombre de fichiers dangereux détectés
        self.toutes_anomalies = []  # Initialiser toutes_anomalies

    # Envoyer au serveur les anomalies de plusieurs fichiers
    def envoyer_anomalies_fichiers_au_serveur(self, anomalies):
        # envoyer les anomalies au serveur
        token = os.getenv("ACCESS_TOKEN")
        headers = {"Authorization": f"Bearer {token}"}
        url = os.getenv("SERVER_ADDRESS") + '/' + get('VARS', 'CLIENT_ID') + '/machine/error'

        anomalies_envoyees = []

        for anomalie in anomalies:
            if anomalie not in anomalies_envoyees:
                continue

            # Construction du message d'erreur
            error_data = {
                'type': anomalie['type'] or 'PROBABLEMENT_SAIN',
                'path': anomalie['path'] or 'Unknown',
                'date': anomalie['date'].isoformat(),
                'message': anomalie['message']
            }
        
            params = {
                "machineAddress": ':'.join(['{:02x}'.format((getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1]),
            }
            
            # Vérifier la réponse
            for _ in range(3):  # Effectuer jusqu'à 3 tentatives
                try:
                    response = requests.post(url, params=params, data=error_data, headers=headers)
                    response.raise_for_status()
                    if response.status_code == 201:
                        print(f"Anomalie pour {anomalie['path']} a été envoyée avec succès.")
                        anomalies_envoyees.append(anomalie)
                        break 
                    else:
                        print(f"Une erreur s'est produite pour {anomalie['path']}: {response.text}")
                        sleep(2)
                except RequestException as e:
                    print(f"Erreur de connexion lors de l'envoi des anomalies : {str(e)}")
                    sleep(2)
                    
            if response.status_code != 201:
                print(f"Échec de l'envoi des anomalies pour {anomalie['path']} après plusieurs tentatives.")
    
    # Analyser un seul fichier dans le système
    def analyser_fichier_unique(self, file: str, extensions: list[str]):
        global nb_anomalies
        if len(self.toutes_anomalies) != 0:
            nb_anomalies += len(self.toutes_anomalies)

        try:
            ## ----------- Test ---------------##
            file_name = os.path.basename(file)
            self.file = file  # Définir le fichier à analyser
            anomalies = []  # Liste pour stocker les anomalies détectées

            # obtenir la date et l'heure actuelle
            date = datetime.now()
            
            # Vérifier l'extension
            if not self.verifier_extension(extensions):
                anomalies.append({
                    'type': 'EXTENSION',
                    'path': os.path.abspath(file),
                    'date': date,
                    'message': f"L'extension du fichier {file_name} ne figure pas dans la base de données de référence."
                })

            # Vérifier si le fichier peut être ouvert
            if not self.verifier_ouverture_fichier():
                anomalies.append({
                    'type': 'OUVERTURE',
                    'path': os.path.abspath(file),
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
                    'path': os.path.abspath(file),
                    'date': date,
                    'message': f"Le fichier {file_name} a une haute entropie ({entropie}). Il est possible qu'il soit chiffré."
                })

            # Vérifier les changements significatifs de taille de fichier
            # La taille de fichier doit changer de plus de 1000 octets = 1 ko pour déclencher une alerte
            size_threshold = 1000
            if Utilitaires.check_file_size(self.file, self.old_sizes, size_threshold):
                anomalies.append({
                    'type': 'TAILLE',
                    'path': os.path.abspath(file),
                    'date': date,
                    'message': f"La taille du fichier {file_name} a changé de manière significative."
                })

            # Vérifier la réputation du fichier
            if self.check_virustotal():
                anomalies.append({
                    'type': 'REPUTATION',
                    'path': os.path.abspath(file),
                    'date': date,
                    'message': f"Le fichier {file_name} est identifié comme malveillant par VirusTotal."
                })

            # Ajouter les anomalies détectées à toutes_anomalies
            self.toutes_anomalies.extend(anomalies)

            # Envoyer les anomalies au serveur
            self.envoyer_anomalies_fichiers_au_serveur(self.toutes_anomalies)
            
            # ajouter au compteur de fichier potentiellement dangereux si une ou plusieurs anomalies
            if anomalies:
                self.fichiers_dangereux += 1

            return True if len(anomalies) > 0 else False
        except Exception as e:
            self.alerte(f"Erreur lors de l'analyse du fichier {file}: {str(e)}")
            return False
     
    # Analyser un dossier complet dans le système
    def analyser_dossier_complet(self, dossier: str):
        global nb_anomalies
        if len(self.toutes_anomalies) != 0:
            nb_anomalies += len(self.toutes_anomalies)
        try:
            fichiers_systeme = Utilitaires.charger_fichier_systeme(dossier)

            for fichier in fichiers_systeme:
                fichier_path = os.path.join(dossier, fichier)
                fichier_abs_path = os.path.abspath(fichier_path)

                if os.path.isdir(fichier_path):
                    # Analyser le sous-dossier de manière récursive
                    self.analyser_dossier_complet(fichier_path)
                else:
                    self.analyser_fichier_unique(fichier_path, self.extensions)

        except Exception as e:
            self.alerte(f"Erreur lors de l'analyse du dossier {dossier}: {str(e)}")

def analyse() -> tuple[bool, str]:
    global nb_anomalies
    try:
        nb_anomalies = 0
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

        for dossier, detection in detections.items():
            print("TOUTES ANOMALIES:", nb_anomalies)
            if nb_anomalies != 0:
                return True, ""
            print(f"\nAnalyse du dossier : {dossier}\n")
            result = detection.analyser_dossier_complet(dossier)
            nb_anomalies += result if result else 0
            print(f"Nombre de fichiers dangereux détectés dans le dossier {dossier} : {detection.fichiers_dangereux}")

        return (True, "") if detection.fichiers_dangereux != 0 else (False, "")
    
    except KeyboardInterrupt:
        return False, ""

