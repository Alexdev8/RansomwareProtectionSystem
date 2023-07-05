import threading
import time
import requests
import os

from ClientApp.DataBackupSystem.backup import full_backup, partial_backup, send_directory_files, get_last_backup
from .DetectionSystem.detection import analyse
from .PCIsolation.network_interface_up_no_loopback import desactivation_interfaces
from .PopUp.popup import message_erreur
from . import load_vars as vars
from dotenv import load_dotenv

load_dotenv()
temp_path = os.getenv('TEMP')

backup_authorization = False

def main():
    def main_analyse():
        while True:
            result = analyse()
            if result[0]:
                # Une erreur a été détecté
                backup_authorization = Falsemessage_erreur(desactivation_interfaces(), result[1])
            else:
                # if sys.argv[1:] and sys.argv[1] == "backup":
                print("Backup autorisé")
            backup_authorization = True

            time.sleep(int(vars.get("VARS", "ANALYSE_FREQUENCY")))


def main_backup():
    while True:
        if backup_authorization:
            response = requests.get(os.environ.get("SERVER_ADDRESS"))

            # Vérifier la réponse
            if response.text == "Ouai, c'est Greg !":

                full_backup(temp_path)
                send_directory_files(get_last_backup(temp_path),
                                     os.environ.get("SERVER_ADDRESS") + '/' + vars.get('VARS',
                                                                                       'CLIENT_ID') + '/backup/push')

            elif response.text == "Ah ouai une petite frerot vasy":

                partial_backup(temp_path)
                send_directory_files(get_last_backup(temp_path),
                                     os.environ.get("SERVER_ADDRESS") + '/' + vars.get('VARS',
                                                                                       'CLIENT_ID') + '/backup/push')

            elif response.text == "Tié zinzin frate":
                print("Aucune backup n'est nécessaire pour le moment")

            else:
                print("Error")
        # wait 5 min
        time.sleep(300)


    analyse_thread = threading.Thread(target=main_analyse)
    backup_thread = threading.Thread(target=main_backup)

    analyse_thread.start()
    backup_thread.start()
