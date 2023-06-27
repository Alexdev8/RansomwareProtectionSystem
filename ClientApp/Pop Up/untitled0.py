import tkinter as tk
from PIL import Image, ImageTk
import os

def close_window(root):
    root.destroy()


def show_special_text(special_text):
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
    image_path = os.path.join(script_dir, "logo.png")
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
    text_x = 10
    text_y = dialog_height // 2

    # Affichage du texte sur le canevas
    canvas.create_text(text_x, text_y, text=special_text, fill='black', font=('Arial', 16), justify='left', width=dialog_width - 20, anchor='w', tags='special_text')





    # Création du bouton OK pour fermer la fenêtre
    button_ok = tk.Button(root, text="OK", width=10, command=lambda: close_window(root))
    button_ok.place(relx=0.5, rely=0.95, anchor='s')  # Placer le bouton en bas au centre

    # Lancement de la boucle principale
    root.mainloop()




# Exemple d'utilisation
Message="Cher utilisateur,"+"\n"+"Nous souhaitons vous informer que vous semblez actuellement victime d'une attaque de ransomware, mais ne vous inquiétez pas, nous somme là pour vous aider."
show_special_text(Message)
