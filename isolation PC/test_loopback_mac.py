import subprocess

def is_loopback(interface):
    cmd = f"ifconfig {interface}"
    return subprocess.check_output(cmd, shell=True, encoding='utf-8')

# Exemple d'utilisation
interface_name = 'lo0'
interface_output = is_loopback(interface_name)
if 'loopback' in interface_output.lower():
    print(f"L'interface {interface_name} est une interface loopback.")
else:
    print(f"L'interface {interface_name} n'est pas une interface loopback.")

print(f"Informations sur l'interface {interface_name}:")
print(interface_output)
