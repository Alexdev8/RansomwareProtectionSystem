import subprocess

def is_loopback_mac(interface):
    cmd = f"ifconfig {interface}"
    output = subprocess.check_output(cmd, shell=True, encoding='utf-8')
    lines = output.split('\n')
    for line in lines:
        if 'loopback' in line:
            return True
    return False

# Exemple d'utilisation
# interface_name = 'lo0'
# interface_output = is_loopback_mac(interface_name)
# if 'loopback' in interface_output.lower():
#    print(f"L'interface {interface_name} est une interface loopback.")
# else:
#    print(f"L'interface {interface_name} n'est pas une interface loopback.")

# print(f"Informations sur l'interface {interface_name}:")
# print(interface_output)
