import sys
import time

from ClientApp.DetectionSystem.detection import analyse
from ClientApp.PCIsolation.network_interface_up_no_loopback import desactivation_interfaces
from ClientApp.PopUp.popup import message_erreur
import ClientApp.load_vars as vars

if sys.argv[1:] and sys.argv[1] == "backup":
    print("c'est le backup là en gros")
    pass
else:
    while True:
        result = analyse()
        print(result)
        if result[0]:
            print(result[1])
            message_erreur(desactivation_interfaces(),"Mettre ici le message du code d'erreur")
        else:
            pass
        time.sleep(int(vars.get("VARS", "ANALYSE_FREQUENCY")))
