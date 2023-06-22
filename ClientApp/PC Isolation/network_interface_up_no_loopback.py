import psutil
import platform
from test_loopback import is_loopback
from test_loopback_mac import is_loopback_mac
from test_loopback_linux import is_loopback_linux
from interface_desactivation import disable_interfaces
from interface_desactivation_linux import disable_interfaces_linux
from interface_desactivation_mac import disable_interfaces_mac

def get_network_interfaces():
    interfaces = []
    for interface, stats in psutil.net_if_stats().items():
        if stats.isup and interface != 'lo':
            interfaces.append(interface)
    return interfaces

# Appel de la fonction pour obtenir les interfaces réseau
network_interfaces = get_network_interfaces()

interfaces_to_disabled = []
# Affichage des noms des interfaces réseau
system = platform.system()
if system == "Windows":
    for interface in network_interfaces:
        if not is_loopback(interface):
            interfaces_to_disabled.append(interface)
    for interface in interfaces_to_disabled:
        disable_interfaces(interface)
if system == "Darwin":
    for interface in network_interfaces:
        if not is_loopback_mac(interface):
            interfaces_to_disabled.append(interface)
    for interface in interfaces_to_disabled:
        disable_interfaces_mac(interface)
if platform.system() == 'Linux':
    for interface in network_interfaces:
        if not is_loopback_linux(interface):
            interfaces_to_disabled.append(interface)
    for interface in interfaces_to_disabled:
        disable_interfaces_linux(interface)
for interface in interfaces_to_disabled:
    disable_interfaces(interface)
