import subprocess

def enable_interfaces_mac(interface):
    cmd = f"ifconfig {interface} up"
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"L'interface \"{interface}\" a été réactivée.")
    except subprocess.CalledProcessError:
        print(f"Erreur lors de la réactivation de l'interface \"{interface}\".")