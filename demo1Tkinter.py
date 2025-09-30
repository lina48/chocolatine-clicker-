import tkinter as tk

# Créer la fenêtre principale
root = tk.Tk()
root.title("Chocolatine Clicker - Démo Tkinter")
root.geometry("720x450")  # Largeur x Hauteur

# Variables
compteur = tk.DoubleVar(value=0)
cps = tk.DoubleVar(value=0)  # Chocolatines par seconde
prix_cps = tk.DoubleVar(value=10)  # Prix initial du bouton CPS
total_chocolatines = tk.DoubleVar(value=0)  # Chocolatines fabriquées depuis le début
cps_increment = 0.1  # Valeur d'ajout du bouton Nouveaux-Née

# Frame pour la ligne du compteur et du bouton spécial
top_frame = tk.Frame(root)
top_frame.pack(pady=20, anchor="w")

# Label pour afficher la valeur du compteur
compteur_label = tk.Label(top_frame, text=f"Chocolatine : {int(compteur.get())}", font=("Arial", 32))
compteur_label.pack(side="left")

# Fonction pour le bouton lvl2 Nouveaux-Née : double l'incrément et supprime le bouton
def activer_lvl2():
    global cps_increment
    cps_increment *= 2
    special_button.destroy()
    cps_button.config(text=f"Nouveaux-Née +{cps_increment:.1f} CPS Prix:{int(prix_cps.get())}")

# Bouton Nouveaux-Née lvl2 , caché au début
special_button = tk.Button(
    top_frame,
    text="Lvl 2 Nouveaux-Née",
    font=("Arial", 16),
    width=18,
    height=2,
    background="black",
    foreground="white",
    command=activer_lvl2
)
# Ne pas pack maintenant, on le fera plus tard

# Nouveau label pour afficher les chocolatines par seconde
cps_label = tk.Label(root, text=f"Chocolatines/sec : {cps.get()}", font=("Arial", 20))
cps_label.pack(pady=10, anchor="w")  # Collé à gauche

# Label pour afficher le total de chocolatines
total_label = tk.Label(root, text=f"Total chocolatines : {int(total_chocolatines.get())}", font=("Arial", 18))
total_label.pack(pady=5, anchor="w")

# Fonction appelée lors du clic sur le bouton
def augmenter():
    compteur.set(compteur.get() + 1)
    total_chocolatines.set(total_chocolatines.get() + 1)
    compteur_label.config(text=f"Chocolatine : {int(compteur.get())}")
    total_label.config(text=f"Total chocolatines : {int(total_chocolatines.get())}")

# Fonction pour ajouter des chocolatines chaque seconde
def ajouter_cps():
    chocolatines_ajoutees = cps.get() / 10
    compteur.set(compteur.get() + chocolatines_ajoutees)
    total_chocolatines.set(total_chocolatines.get() + chocolatines_ajoutees)
    compteur_label.config(text=f"Chocolatine : {int(compteur.get())}")
    total_label.config(text=f"Total chocolatines : {int(total_chocolatines.get())}")
    # Afficher le bouton spécial si le total atteint 100
    if total_chocolatines.get() >= 100 and not special_button.winfo_ismapped():
        special_button.pack(side="left", padx=10)
    root.after(100, ajouter_cps)

# Fonction pour augmenter le cps
def augmenter_cps():
    global cps_increment
    if compteur.get() >= prix_cps.get():
        compteur.set(compteur.get() - prix_cps.get())
        cps.set(round(cps.get() + cps_increment, 1))
        # Augmenter le prix de 10%
        nouveau_prix = round(prix_cps.get() * 1.1, 1)
        prix_cps.set(nouveau_prix)
        compteur_label.config(text=f"Chocolatine : {int(compteur.get())}")
        cps_button.config(text=f"Nouveaux-Née +{cps_increment:.1f} CPS Prix:{int(prix_cps.get())}")
        cps_label.config(text=f"Chocolatines/sec : {cps.get()}")

# Frame pour aligner les boutons horizontalement à gauche
button_frame = tk.Frame(root)
button_frame.pack(pady=20, anchor="w")

# Bouton fabriquer chocolatine (à gauche)
fabriquer_button = tk.Button(button_frame, text="Fabriquer Chocolatine", command=augmenter, font=("Arial", 24), width=20, height=2, background="orange", foreground="White")
fabriquer_button.pack(side="left")

# Bouton pour augmenter le cps (à droite du bouton fabriquer)
cps_button = tk.Button(
    button_frame,
    text=f"Nouveaux-Née +{cps_increment:.1f} CPS Prix:{int(prix_cps.get())}",
    command=augmenter_cps,
    font=("Arial", 16),
    width=28,
    height=2,
    background="lightblue"
)
cps_button.pack(side="left", padx=10)

# Démarrer l'ajout automatique
ajouter_cps()

# Boucle principale
root.mainloop()