import tkinter as tk

MicheMiche=True
erreur="Cher utilisateur,"+"\n"+" Nous regrettons de vous informer qu'une erreur est survenue lors de votre interaction avec notre système."+"\n"+" Veuillez accepter nos excuses les plus sincères pour les désagréments causés."+"\n"+" Nous comprenons l'importance de votre expérience utilisateur et nous nous engageons à résoudre ce problème dans les plus brefs délais."+"\n"+ "Nos équipes techniques ont été informées de cette erreur et travaillent activement à sa résolution. "+"\n"+"Nous vous remercions de votre patience pendant que nous cherchons la meilleure solution pour rectifier cette situation."+"\n"+ "Nous vous encourageons à réessayer ultérieurement."+"\n"+ "En attendant, veuillez vérifier les points suivants pour vous assurer qu'il ne s'agit pas d'une erreur de configuration de votre part :"


# Fonction pour afficher le texte spécial
import os
from PIL import Image, ImageTk
import threading
import pygame

def jouer_audio(fichier_audio):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(fichier_audio)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            continue

    except pygame.error as err:
        print("Une erreur s'est produite :", err)

    pygame.mixer.quit()
    pygame.quit()

def close_window(root):
    root.destroy()
def show_special_text(special_text):
    # Création de la fenêtre principale
    root = tk.Tk()
    root.resizable(False, False)
    root.overrideredirect(True)

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

    # Chargement deu logo
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


    # Chargement de l'image "Alex.jpeg"
    image_path2 = os.path.join(script_dir, "Alex.jpeg")
    logo_image2 = Image.open(image_path2)
    logo_image2 = logo_image2.resize((100, 100), Image.LANCZOS)  # Ajustez la taille de l'image selon vos besoins
    logo_photo2 = ImageTk.PhotoImage(logo_image2)

    # Calcul des coordonnées pour positionner la deuxième image
    image2_x = 10  # Décalage horizontal à partir du coin supérieur gauche
    image2_y = 10  # Décalage vertical à partir du coin supérieur gauche
    # Affichage de la deuxième image sur le canevas
    canvas.create_image(image2_x, image2_y, anchor='nw', image=logo_photo2)

    # Chargement de l'image "Alexis.jpeg"
    image_path3 = os.path.join(script_dir, "alexis.jpeg")
    logo_image3 = Image.open(image_path3)
    logo_image3 = logo_image3.resize((100, 100), Image.LANCZOS)  # Ajustez la taille de l'image selon vos besoins
    logo_photo3 = ImageTk.PhotoImage(logo_image3)

    image3_x = dialog_width - image_width
    image3_y = 0
    canvas.create_image(image3_x, image3_y, anchor='ne', image=logo_image3)



    # Calcul des coordonnées pour afficher le texte centré
    text_x = dialog_width // 2
    text_y = dialog_height // 2

    # Affichage du texte sur le canevas
    canvas.create_text(text_x, text_y, text=special_text, fill='black', font=('Arial', 16), justify='center')

    # Fonction pour fermer la fenêtre




    # Création du bouton OK pour fermer la fenêtre
    button_ok = tk.Button(root, text="OK", width=10, command=lambda: close_window(root))
    button_ok.place(relx=0.5, rely=0.95, anchor='s')  # Placer le bouton en bas au centre

    # Lancement de la boucle principale
    root.mainloop()


# Exemple d'utilisation


# Appel de la fonction pour afficher le texte spécial
if MicheMiche==True:
    fichier_audio = "menace.mp3"
    audio_thread = threading.Thread(target=jouer_audio, args=(fichier_audio,))
    text_thread = threading.Thread(target=show_special_text, args=(erreur,))

    audio_thread.start()
    text_thread.start()

    audio_thread.join()
    text_thread.join()
    show_special_text(erreur)







