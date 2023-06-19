import subprocess

def is_loopback(interface):
    cmd = f"netsh interface ip show address \"{interface}\""
    output = subprocess.check_output(cmd, shell=True, encoding='cp850').lower()
    lines = output.split('\n')
    for line in lines:
        if 'loopback' in line:
            return True
    return False

# Exemple d'utilisation
interface_name = 'lo0'
is_loopback_interface = is_loopback(interface_name)

if is_loopback_interface:
    print(f"L'interface {interface_name} est une interface loopback.")
else:
    print(f"L'interface {interface_name} n'est pas une interface loopback.")
