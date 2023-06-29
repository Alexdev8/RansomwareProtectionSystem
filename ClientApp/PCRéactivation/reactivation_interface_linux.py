import subprocess

def enable_interfaces_linux(interface):
    cmd = f"ip link set {interface} up"
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"L'interface \"{interface}\" a été réactivé.")
    except subprocess.CalledProcessError:
        print(f"Erreur lors de la réactivation de l'interface \"{interface}\".")