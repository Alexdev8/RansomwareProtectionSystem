import subprocess

def enable_interfaces(interface):
    cmd = f"netsh interface set interface \"{interface}\" admin=enable"
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"L'interface \"{interface}\" a été réactivé.")
    except subprocess.CalledProcessError:
        print(f"Erreur lors de la réactivation de l'interface \"{interface}\".")