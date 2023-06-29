import subprocess

def disable_interfaces(interface):
    cmd = f"netsh interface set interface \"{interface}\" admin=disable"
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"L'interface \"{interface}\" a été désactivée.")
    except subprocess.CalledProcessError:
        print(f"Erreur lors de la désactivation de l'interface \"{interface}\".")

# Appeler la fonction pour désactiver la connexion Wi-Fi
# disable_interfaces("Wi-Fi")