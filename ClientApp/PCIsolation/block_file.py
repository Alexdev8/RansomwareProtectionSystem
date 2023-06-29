import os
def block_file(absolute_path):
    # Définir les permissions pour bloquer l'accès en lecture et en exécution
    os.chmod(absolute_path, 0o000)

    # Vérifier les nouvelles permissions
    permissions = oct(os.stat(absolute_path).st_mode)[-3:]
    print("Permissions du fichier :", permissions)

# test
block_file(r"C:\Users\yaelb\Downloads\test_factory.txt")