import threading
import time
import requests
import re
import uuid
import os

from .DataBackupSystem.backup import full_backup, partial_backup, send_directory_files, get_last_backup
from .DetectionSystem.detection2 import analyse
from .PCIsolation.network_interface_up_no_loopback import desactivation_interfaces
from .PopUp.popup import message_erreur
from . import load_vars as vars
from dotenv import load_dotenv

load_dotenv('.env')
temp_path = os.getenv('BACKUP_TEMP_PATH')

backup_authorization = False


def main():
    def main_analyse():
        global backup_authorization
        while True:
            result = analyse()
            if result[0]:
                # Une erreur a été détecté
                backup_authorization = False
                message_erreur(desactivation_interfaces(), result[1])
            else:
                # if sys.argv[1:] and sys.argv[1] == "backup":
                backup_authorization = True

            time.sleep(int(vars.get("VARS", "ANALYSE_FREQUENCY")))

    def main_backup():
        while True:
            if backup_authorization:
                headers = {"Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"}
                url = os.environ.get("SERVER_ADDRESS") + '/' + vars.get('VARS', 'CLIENT_ID') + '/backup/push'
                params = {
                    "machineAddress": ':'.join(re.findall('..', '%012x' % uuid.getnode()))
                }

                response = requests.get(url, headers=headers, params=params)

                # Vérifier la réponse
                if response.text == "Ouai, c'est Greg !":
                    print("Full backup")
                    full_backup(temp_path)
                    send_directory_files(get_last_backup(temp_path),
                                         os.environ.get("SERVER_ADDRESS") + '/' + vars.get('VARS',
                                                                                           'CLIENT_ID') + '/backup/push')

                elif response.text == "Ah ouai une petite frerot vasy":
                    print("Partial backup")
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
