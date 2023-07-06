import os
import tkinter as tk
from PIL import Image, ImageTk
from dotenv import load_dotenv
import load_vars as vars
from PCRéactivation.network_interfaces_to_up import interfaces_to_up


def close_window(root):
    root.destroy()

def submit():
    global username_entry, password_entry  # Déclarer les variables en tant que globales
    username = username_entry.get()
    password = password_entry.get()
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    print(vars.get("VARS","CLIENT_ID"),os.environ.get('ACCESS_TOKEN'))
    if username==vars.get("VARS","CLIENT_ID") and password==os.environ.get('ACCESS_TOKEN'):

        close_window(root)
        close_window(connection)
        interfaces_to_up(interfaces_to_enable)
from tkinter import ttk

def afficher_texte(texte):
    erreur = tk.Tk()
    erreur.wm_attributes("-topmost", 1)

    # Créez le canevas pour afficher le texte et la barre de défilement
    canvas = tk.Canvas(erreur, width=dialog_width, height=dialog_height, bg='blue')
    canvas.pack(side="left", fill="both")

    # Créez un widget de texte pour afficher le texte
    text_widget = tk.Text(canvas, font=('Arial', 16), wrap='word',bg="black",fg="red")
    text_widget.insert(tk.END, texte)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Attachez la barre de défilement au widget de texte
    scrollbar = ttk.Scrollbar(erreur, command=text_widget.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget.configure(yscrollcommand=scrollbar.set)

    # Appliquez le style de barre de défilement
    style = ttk.Style()
    style.configure("TScrollbar", gripcount=0, background="gray")
    style.map("TScrollbar", background=[("active", "gray")])

    erreur.mainloop()




def message_erreur(interfaces,texte):

    global interfaces_to_enable,screen_width,screen_height,text_x,text_y,code_erreur,x,y,candas,dialog_width,dialog_height,root
    code_erreur=texte
    interfaces_to_enable = interfaces
    special_text="Cher utilisateur,"+"\n"+"Nous souhaitons vous informer que vous semblez actuellement victime d'une attaque de ransomware, mais ne vous inquiétez pas, nous somme là pour vous aider."+"\n\n\n"+"L'administrateur a était contacté"

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
    image_height = int(dialog_height * 0.3)  # Utiliser 20% de la hauteur totale de la fenêtre
    image_width = int(image_height * logo_image.width / logo_image.height)  # Calculer la largeur proportionnelle
    logo_image = logo_image.resize((image_width, image_height), Image.LANCZOS)  # Redimensionner l'image
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
    canvas.create_text(text_x, text_y, text=special_text, fill='black', font=('Arial', 16), justify='center', width=int(dialog_width * 0.8), anchor='center', tags='special_text')





    # Création du bouton OK pour fermer la fenêtre
    button_ok = tk.Button(root, text="Plus de détails", width=15, command=lambda: afficher_texte(code_erreur))
    button_ok.place(relx=0.6, rely=0.95, anchor='s')  # Placer le bouton en bas au centre
    # Création du bouton OK pour fermer la fenêtre
    button_ok = tk.Button(root, text="Administrateur", width=15, command=lambda: ConnectionAdmin())
    button_ok.place(relx=0.4, rely=0.95, anchor='s')  # Placer le bouton en bas au centre

    # Lancement de la boucle principale
    root.mainloop()


def ConnectionAdmin():
    global connection
    connection = tk.Tk()
    global username_entry, password_entry
    connection.wm_attributes("-topmost", 1)  # Garder la fenêtre au premier plan
    connection.title("Connexion Administrateur")

    # Calcul des dimensions pour la taille de la fenêtre
    screen_width = connection.winfo_screenwidth()
    screen_height = connection.winfo_screenheight()
    dialog_width = int(screen_width * 0.2)
    dialog_height = int(screen_height * 0.15)


    # Positionnement de la fenêtre au centre de l'écran
    x = (screen_width - dialog_width) // 2
    y = (screen_height - dialog_height) // 2
    connection.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    username_label = tk.Label(connection, text="Identifiant client:")
    password_label = tk.Label(connection, text="Token:")


    username_entry = tk.Entry(connection,font=('Arial', 16),width=30)
    password_entry = tk.Entry(connection, show="*", font=('Arial', 16),width=30)  # Les caractères du mot de passe seront masqués avec des étoiles
    username_entry.place(relx=0.5,rely=0.4)
    password_entry.place(relx=0.5,rely=0.5)

    # Création du bouton de soumission
    submit_button = tk.Button(connection, text="Valider", command=submit)
    submit_button.place(relx=0.5, rely=0.95, anchor='s')  # Placer le bouton en bas au centre

    # Placement des éléments dans la fenêtre
    username_label.pack()
    username_entry.pack()
    password_label.pack()
    password_entry.pack()
    submit_button.pack()


    connection.mainloop()


message_erreur([],"")
