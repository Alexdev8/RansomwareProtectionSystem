import os
import tkinter as tk
from PIL import Image, ImageTk
from dotenv import load_dotenv
import ClientApp.load_vars as vars



load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
A= os.environ.get('ACCESS_TOKEN')
b=vars.get("VARS","CLIENT_ID")
print(A,b)





def close_window(root):
    root.destroy()

def submit():
    global username_entry, password_entry  # Déclarer les variables en tant que globales
    username = username_entry.get()
    password = password_entry.get()
    print("Identifiant:", username)
    print("Mot de passe:", password)

def Message_Erreur(special_text):
    # Création de la fenêtre principale
    root = tk.Tk()
    root.resizable(False, False)
    root.overrideredirect(True)
    root.wm_attributes("-topmost", 1)  # Garder la fenêtre au premier plan
    # Calcul des dimensions pour la taille de la fenêtre
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    dialog_width = int(screen_width * 0.6)
    dialog_height = int(screen_height * 0.6)

    # Positionnement de la fenêtre au centre de l'écran
    x = (screen_width - dialog_width) // 2
    y = (screen_height - dialog_height) // 2
    root.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    # Création du canevas (canvas)
    canvas = tk.Canvas(root, width=dialog_width, height=dialog_height, bg='light blue')
    canvas.pack()

    # Obtention du chemin absolu du script Python
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Chargement du logo
    image_path = os.path.join(script_dir, "RPS.png")
    logo_image = Image.open(image_path)
    logo_image = logo_image.resize((200, 200), Image.LANCZOS)  # Ajustez la taille de l'image selon vos besoins
    logo_photo = ImageTk.PhotoImage(logo_image)
    # Calcul des coordonnées pour centrer le logo
    image_width = logo_image.width
    image_height = logo_image.height
    image_x = (dialog_width - image_width) // 2
    # Affichage de la première image centrée sur le canevas
    canvas.create_image(image_x, 0, anchor='nw', image=logo_photo)




    # Calcul des coordonnées pour afficher le texte centré
    text_x = dialog_width // 2
    text_y = dialog_height // 2

    # Affichage du texte sur le canevas
    canvas.create_text(text_x, text_y, text=special_text, fill='black', font=('Arial', 16), justify='center', width=dialog_width - 20, anchor='center',                        tags='special_text')





    # Création du bouton OK pour fermer la fenêtre
    button_ok = tk.Button(root, text="Kill", width=10, command=lambda: close_window(root))
    button_ok.place(relx=0.6, rely=0.95, anchor='s')  # Placer le bouton en bas au centre
    # Création du bouton OK pour fermer la fenêtre
    button_ok = tk.Button(root, text="Admin ?", width=10, command=lambda: ConnectionAdmin())
    button_ok.place(relx=0.4, rely=0.95, anchor='s')  # Placer le bouton en bas au centre

    # Lancement de la boucle principale
    root.mainloop()

def ConnectionAdmin():
    global username_entry, password_entry
    connection = tk.Tk()
    connection.resizable(True, True)
    connection.overrideredirect(True)
    connection.wm_attributes("-topmost", 1)  # Garder la fenêtre au premier plan

    # Calcul des dimensions pour la taille de la fenêtre
    screen_width = connection.winfo_screenwidth()
    screen_height = connection.winfo_screenheight()
    dialog_width = int(screen_width * 0.2)
    dialog_height = int(screen_height * 0.2)


    # Positionnement de la fenêtre au centre de l'écran
    x = (screen_width - dialog_width) // 2
    y = (screen_height - dialog_height) // 2
    connection.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    username_label = tk.Label(connection, text="Identifiant client:")
    password_label = tk.Label(connection, text="Token:")

    username_entry = tk.Entry(connection)
    password_entry = tk.Entry(connection, show="*")  # Les caractères du mot de passe seront masqués avec des étoiles

    # Création du bouton de soumission
    submit_button = tk.Button(connection, text="Valider", command=submit)

    # Placement des éléments dans la fenêtre
    username_label.pack()
    username_entry.pack()
    password_label.pack()
    password_entry.pack()
    submit_button.pack()


    button_ok = tk.Button(connection, text="Kill", width=10, command=lambda: close_window(connection))
    button_ok.place(relx=0.5, rely=0.95, anchor='s')  # Placer le bouton en bas au centre
    connection.mainloop()


#a=vars.get("VARS","CLIENT_ID")
#print(a)
# Exemple d'utilisation
Message="Cher utilisateur,"+"\n"+"Nous souhaitons vous informer que vous semblez actuellement victime d'une attaque de ransomware, mais ne vous inquiétez pas, nous somme là pour vous aider."+"\n\n\n"+"Veuillez contacter votre administrateur"
Message_Erreur(Message)
