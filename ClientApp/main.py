import threading
import time

from ClientApp.DetectionSystem.detection import analyse
from ClientApp.PCIsolation.network_interface_up_no_loopback import desactivation_interfaces
from ClientApp.PopUp.popup import message_erreur
import ClientApp.load_vars as vars

def main_analyse():
    while True:
        result = analyse()
        print(result)
        if result[0]:
            # Une erreur a été détecté
            message_erreur(desactivation_interfaces(), result[1])
        else:
            # if sys.argv[1:] and sys.argv[1] == "backup":
            print("c'est le backup là en gros")

        time.sleep(int(vars.get("VARS", "ANALYSE_FREQUENCY")))

def main_backup():
    for i in range(100):
        print("yo")
        time.sleep(0.5)

analyse_thread = threading.Thread(target=main_analyse)
backup_thread = threading.Thread(target=main_backup)

analyse_thread.start()
backup_thread.start()
