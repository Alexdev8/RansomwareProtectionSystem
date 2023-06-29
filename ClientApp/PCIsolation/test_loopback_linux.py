import subprocess

def is_loopback_linux(interface):
    cmd = f"ip addr show dev {interface}"
    output = subprocess.check_output(cmd, shell=True, encoding='utf-8')
    return 'LOOPBACK' in output

# Exemple d'utilisation
# interface_name = 'lo'
# is_loopback_interface = is_loopback_linux(interface_name)

# if is_loopback_interface:
#     print(f"L'interface {interface_name} est une interface loopback.")
# else:
#     print(f"L'interface {interface_name} n'est pas une interface loopback.")
