# chocolatine_clicker.py
# chocolatine_clicker_builds.py
import pygame
import sys
import json
from math import ceil
import constants.buildtypes as types
import constants.builds as builds_const
builds = builds_const.builds
import constants.upgrades as upgrades_const
upgrades = [dict(u, bought=False) for u in upgrades_const.upgrades]
# ---------- Paramètres ----------
SAVE_FILE = "chocolatine_builds_save.json"
WIDTH, HEIGHT = 1000, 600
FPS = 60  # pour limiter le nombre d'images à diffuser dans l'exécution du jeu

# ---------- état initial du jeu ----------
state = {
    "count": 0.0,
    "per_click": 1.0,
}
# --- Ajout stats ---
show_stats = False
start_time = pygame.time.get_ticks()
clicks_total = 0

# ---------- formate le nombre pour l'afficher d'une certaine manière (comme 1.2 K, 2 M) ----------
def format_num(n):
    if n < 1000: return f"{n:.0f}"
    if n < 1_000_000: return f"{n/1000:.2f}K"
    if n < 1_000_000_000: return f"{n/1_000_000:.2f}M"
    return f"{n/1_000_000_000:.2f}B"

# calcule le nombre de chocolatines par seconde (CPS) en fonction des bâtiments possédés (générées automatiquement)
# cette fonction parcourt la liste des builds et calcule le CPS total en multipliant le nombre de chaque bâtiment possédé par son boost CPS.
def total_cps():
    return sum(b["owned"] * b["boost"] for b in builds)

# sauvegarde l'état du jeu dans un fichier JSON
# écrit dans un fichier le dictionnaire contenant l'état actuel du jeu (nombre de chocolatines, bâtiments possédés donc state et builds) en utilisant la bibliothèque json.
def save_game():
    try:
        # remove surfaces (images) before saving
        ups = []
        for u in upgrades:
            copy = {k: v for k, v in u.items() if k != "surface"}
            ups.append(copy)
        with open(SAVE_FILE, "w") as f:
            json.dump({"state": state, "builds": builds, "upgrades": ups}, f)
        print("Game saved.")
    except Exception as e:
        print("Save failed:", e)

# charge l'état du jeu à partir d'un fichier JSON
# lit les données depuis save file et met à jour l'état du jeu (state et builds) avec les valeurs chargées.
def load_game():
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        state.update(data.get("state", {}))
        for i, b in enumerate(data.get("builds", builds)):
            builds[i].update(b)
        # load upgrades state if present
        ups = data.get("upgrades")
        if ups:
            for i, u in enumerate(ups):
                if i < len(upgrades):
                    upgrades[i].update(u)
        print("Save loaded.")
    except FileNotFoundError:
        print("No save found; starting fresh.")
    except Exception as e:
        print("Failed to load save:", e)

def build_cost(build):
    # le coût d'un build augmente de 15% à chaque achat par rapport au coût initial
    return round(build["cost"] * (1.15 ** build["owned"]))

# coût d'un upgrade (statique)
def upgrade_cost(upg):
    return upg.get("cost", 0)


def apply_upgrade(upg):
    """Applique l'effet d'un upgrade déjà acheté.
    Double le boost des builds dont le type correspond à l'upgrade."""
    t = upg.get("type")
    if not t:
        return
    for b in builds:
        if b.get("type") == t:
            b["boost"] *= 2
# Les stastistiques
def draw_stats(screen, font, state_dict, clicks_total, start_time):
    screen.fill((30, 30, 30))  # fond sombre
    elapsed = (pygame.time.get_ticks() - start_time) / 1000  # en secondes

    # total CPS depuis les builds
    total_cps = sum(b["owned"] * b["boost"] for b in state_dict["builds"])

    stats_lines = [
        f"=== STATISTIQUES ===",
        f"Chocolatines actuelles : {state_dict['state']['count']:.1f}",
        f"Chocolatines par clic : {state_dict['state']['per_click']:.1f}",
        f"CPS total (auto) : {total_cps:.2f}",
        f"Nombre de clics : {clicks_total}",
        f"Temps de jeu : {elapsed:.1f} sec",
        "",
        "Détails des upgrades :"
    ]

    # affichage des builds
    for b in state_dict["builds"]:
        stats_lines.append(
            f"{b['name']} : {b['owned']} (Boost {b['boost']}/u, total {b['owned']*b['boost']})"
        )

    stats_lines.append("")
    stats_lines.append("Appuyez sur 2 pour revenir au jeu")

    # rendu texte
    for i, line in enumerate(stats_lines):
        text = font.render(line, True, (220, 220, 220))
        screen.blit(text, (50, 80 + i * 30))

# ---------- pygame setup ----------
pygame.init()
# Initialisation de Pygame
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background_color = (235, 205, 169)
screen.fill(background_color)
pygame.display.set_caption("Chocolatine Clicker ")
# time clock pour gérer le framerate pour que le jeu ne tourne pas trop vite
clock = pygame.time.Clock()
# les fonctions pour afficher les polices du texte
font_big = pygame.font.SysFont(None, 48)
font_med = pygame.font.SysFont(None, 28)
font_small = pygame.font.SysFont(None, 20)

# Boutons
# zone cliquable pour la chocolatine sauvegarde et chargement
choco_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 200, 400, 400)
# les boutons de construction de builds sont générés en fonction du nombre de types de bâtiments définis dans la liste builds.
build_buttons_rects = [pygame.Rect(50, 150 + i * 80, 300, 60) for i in range(len(builds))]
# rects pour upgrades (droite)
upgrade_buttons_rects = [pygame.Rect(WIDTH - 360, 50 + i * 80, 300, 60) for i in range(len(upgrades))]
# boutons de sauvegarde et de chargement
save_rect = pygame.Rect(WIDTH - 170, HEIGHT - 140, 120, 40)
load_rect = pygame.Rect(WIDTH - 170, HEIGHT - 80, 120, 40)

# Load save
load_game()
upgrade_to_show = None
# Timing
last_time = pygame.time.get_ticks()
running = True
while running:

    dt_ms = clock.tick(FPS)
    dt = dt_ms / 1000.0

    # Auto CPS
    state["count"] += total_cps() * dt
    # ajoute au compteur de chocolatines le nombre généré automatiquement par les bâtiments possédés, en fonction du temps écoulé depuis la dernière mise à jour.
    # quitte le jeu et sauvegarde l'état actuel du jeu avant de fermer la fenêtre.

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            running = False
        # ajoute des chocolatines au compteur lorsqu'on clique sur l'image de la chocolatine ou appuie sur la barre d'espace.
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # clic chocolatine
            if choco_rect.collidepoint(mx, my):
                state["count"] += state["per_click"]

            # clic builds, parcourt la liste des bâtiments et vérifie si l'utilisateur a cliqué sur l'un des boutons de construction.
            for i, build in enumerate(builds):
                rect = build_buttons_rects[i]
                if rect.collidepoint(mx, my):
                    cost = build_cost(build)
                    # si l'utilisateur a suffisamment de chocolatines pour acheter le bâtiment, le nombre de chocolatines est décrémenté du coût du bâtiment et le nombre de bâtiments possédés est incrémenté de 1.
                    if state["count"] >= cost:
                        state["count"] -= cost
                        build["owned"] += 1

            # clic upgrades: seulement la première non achetée, au même endroit
            if upgrade_to_show:
                rect = upgrade_buttons_rects[0]  # Toujours au même endroit
                if rect.collidepoint(mx, my):
                    cost = upgrade_cost(upgrade_to_show)
                    if state["count"] >= cost:
                        state["count"] -= cost
                        upgrade_to_show["bought"] = True
                        apply_upgrade(upgrade_to_show)

            # save et load boutons
            if save_rect.collidepoint(mx, my):
                save_game()
            if load_rect.collidepoint(mx, my):
                load_game()
        


        # gère les entrées clavier pour cliquer sur la chocolatine (espace), sauvegarder (S) et charger (L).
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                state["count"] += state["per_click"]
            elif event.key == pygame.K_s:
                save_game()
            elif event.key == pygame.K_l:
                load_game()
            elif event.key == pygame.K_2:# ajout une touche pour les stats
                show_stats = not show_stats
        # --- Page STATISTIQUES ---
    if show_stats:

        draw_stats(screen, font_med, {"state": state, "builds": builds}, clicks_total, start_time)
        pygame.display.flip()
        continue

    # mettre à jour l'affichage du jeu
    screen.fill((250, 240, 230))  # background

    # Chocolatine
    choco_image = pygame.image.load("assets/img/chocolatine-removebg-preview.png")
    choco_image = pygame.transform.scale(choco_image, (choco_rect.width, choco_rect.height))  # Ajuster à la taille de choco_rect
    # Afficher l'image de la chocolatine
    screen.blit(choco_image, choco_rect)

    # affichage du nombre de chocolatines, du nombre par clic et du CPS total
    count_text = font_big.render(f"{format_num(state['count'])} chocolatines", True, (40, 30, 20))
    screen.blit(count_text, (50, 30))

    # affichage du nombre de chocolatines par clic et du CPS total
    stats_text = font_med.render(f"Par clic: {state['per_click']:.0f}   CPS (auto): {total_cps():.2f}", True, (40, 30, 20))
    screen.blit(stats_text, (50, 90))

    # parcourt les boutons de construction et dessine chaque bouton avec les informations sur le bâtiment (nom, coût, boost CPS, nombre possédé).
    # affiche le nom de la construction, le nombre possédé et le coût, et le boost CPS de chaque bâtiment.
    for i, build in enumerate(builds):
        rect = build_buttons_rects[i]
        pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=8)
        title = font_med.render(build["name"], True, (50, 10, 10))
        owned = font_small.render(f"Owned: {build['owned']}", True, (200, 10, 10))
        cost_text = font_small.render(f"Cost: {format_num(build_cost(build))}", True, (10, 10, 10))
        boost_text = font_small.render(f"+{build['boost']} CPS", True, (10, 10, 10))
        screen.blit(title, (rect.x + 10, rect.y + 5))
        screen.blit(owned, (rect.x + 10, rect.y + 30))
        screen.blit(cost_text, (rect.x + 120, rect.y + 5))
        screen.blit(boost_text, (rect.x + 120, rect.y + 30))

    # --- Affichage d'une seule upgrade au même endroit ---
    # Cherche la première upgrade non achetée
    upgrade_to_show = None
    upgrade_index = None
    for i, upg in enumerate(upgrades):
        if not upg.get("bought"):
            upgrade_to_show = upg
            upgrade_index = i
            break

    if upgrade_to_show:
        rect = upgrade_buttons_rects[0]  # Toujours au même endroit (le premier bouton)
        pygame.draw.rect(screen, (220, 220, 200), rect, border_radius=8)
        title = font_med.render(upgrade_to_show.get("name", ""), True, (10, 10, 10))
        cost_text = font_small.render(f"Cost: {format_num(upgrade_cost(upgrade_to_show))}", True, (10, 10, 10))
        screen.blit(title, (rect.x + 10, rect.y + 5))
        screen.blit(cost_text, (rect.x + 10, rect.y + 30))

    # Save/load boutons
    pygame.draw.rect(screen, (180, 220, 180), save_rect, border_radius=6)
    pygame.draw.rect(screen, (180, 200, 220), load_rect, border_radius=6)
    screen.blit(font_small.render("Sauvegarder(S)", True, (10, 10, 10)), (save_rect.x + 12, save_rect.y + 10))
    screen.blit(font_small.render("Charger (L)", True, (10, 10, 10)), (load_rect.x + 12, load_rect.y + 10))

    # affiche les instructions pour le joueur en bas de l'écran.
    hint = font_small.render("Cliquez sur la chocolatine ou appuyez sur ESPACE. Sauvegarder avec S. Charger avec L. Statstique avec 2", True, (80, 70, 60))
    screen.blit(hint, (50, HEIGHT - 40))
    # actualise l'affichage de la fenêtre du jeu pour refléter les changements apportés lors de cette itération de la boucle principale.
    pygame.display.flip()

pygame.quit()
sys.exit()