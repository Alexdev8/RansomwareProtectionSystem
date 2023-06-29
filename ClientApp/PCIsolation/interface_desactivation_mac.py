import subprocess

def disable_interfaces_mac(interface):
    cmd = f"ifconfig {interface} down"
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"L'interface \"{interface}\" a été désactivée.")
    except subprocess.CalledProcessError:
        print(f"Erreur lors de la désactivation de l'interface \"{interface}\".")