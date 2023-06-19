import psutil
import platform
system = platform.system()
from test_loopback import is_loopback
from test_loopback_mac import is_loopback_mac
from désactivation_interfaces import disable_interfaces

def get_network_interfaces():
    interfaces = []
    for interface, stats in psutil.net_if_stats().items():
        if stats.isup and interface != 'lo':
            interfaces.append(interface)
    return interfaces

# Appel de la fonction pour obtenir les interfaces réseau
network_interfaces = get_network_interfaces()

interfaces_à_désactivé = []
# Affichage des noms des interfaces réseau

if system == "Windows":
    for interface in network_interfaces:
        if not is_loopback(interface):
            interfaces_à_désactivé.append(interface)
if system == "Darwin":
    for interface in network_interfaces:
        if not is_loopback_mac(interface):
            interfaces_à_désactivé.append(interface)
for interface in interfaces_à_désactivé:
    disable_interfaces(interface)
