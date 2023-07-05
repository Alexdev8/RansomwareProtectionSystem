import platform
from ..PCRéactivation.reactivation_interface import enable_interfaces
from ..PCRéactivation.reactivation_interface_linux import enable_interfaces_linux
from ..PCRéactivation.reactivation_interface_mac import enable_interfaces_mac

def interfaces_to_up(interfaces_to_enable):
    system = platform.system()
    if system == "Windows":
        for interface in interfaces_to_enable:
            enable_interfaces(interface)
    if system == "Darwin":
        for interface in interfaces_to_enable:
            enable_interfaces_linux(interface)
    if system == 'Linux':
        for interface in interfaces_to_enable:
            enable_interfaces_mac(interface)