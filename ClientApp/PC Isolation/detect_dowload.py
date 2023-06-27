import os
import time

def detect_download():
    download_folder = os.path.expanduser("~\Downloads")  # Chemin du dossier de téléchargement sur Windows

    # Obtenir la liste des fichiers actuels dans le dossier de téléchargement
    files_before = set(os.listdir(download_folder))

    while True:
        time.sleep(1)  # Attendre une seconde

        # Obtenir la liste des fichiers après une seconde
        files_after = set(os.listdir(download_folder))

        # Vérifier s'il y a de nouveaux fichiers ajoutés
        new_files = files_after - files_before
        if new_files:
            print("Nouveaux fichiers téléchargés :")
            for file in new_files:
                print(file)

        # Mettre à jour la liste des fichiers avant la prochaine itération
        files_before = files_after

# Appeler la fonction pour détecter les téléchargements
detect_download()