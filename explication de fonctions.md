Projet : Chocolatine Clicker 

Introduction
Le projet « Chocolatine Clicker » est un jeu développé avec la bibliothèque Pygame. Il s’inspire du concept de jeu de type clicker, où l’utilisateur doit cliquer sur une image de chocolatine pour accumuler des points, appelés ici des chocolatines. Ces points permettent ensuite d’acheter des bâtiments et des améliorations qui augmentent le nombre de chocolatines générées automatiquement par seconde (CPS). Le projet inclut également un système de sauvegarde et de chargement, ainsi qu’une page de statistiques.
Extraits de code et explications
1. État initial du jeu

state = {
    "count": 0.0,
    "per_click": 1.0,
}

Ce dictionnaire représente l’état initial du jeu : le nombre de chocolatines disponibles (count ) et le nombre de chocolatines gagnées par clic (per_click ).
2. Fonction de formatage des nombres

def format_num(n):
    if n < 1000: return f"{n:.0f}"
    if n < 1_000_000: return f"{n/1000:.2f}K"
    if n < 1_000_000_000: return f"{n/1_000_000:.2f}M"
    return f"{n/1_000_000_000:.2f}B"

Cette fonction permet d’afficher les grands nombres sous une forme abrégée (par exemple : 1.2K, 3.5M), afin de rendre l’affichage plus lisible pour le joueur.
3. Sauvegarde et chargement

def save_game():
    with open(SAVE_FILE, "w") as f:
        json.dump({"state": state, "builds": builds, "upgrades": upgrades}, f)

def load_game():
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    state.update(data.get("state", {}))
    for i, b in enumerate(data.get("builds", builds)):
        builds[i].update(b)

Ces fonctions permettent respectivement de sauvegarder l’état du jeu dans un fichier JSON et de le recharger. Cela assure la persistance des données entre plusieurs sessions de jeu.
4. Statistiques

def draw_stats(screen, font, state_dict, clicks_total, start_time):
    elapsed = (pygame.time.get_ticks() - start_time) / 1000
    total_cps = sum(b["owned"] * b["boost"] for b in state_dict["builds"])
    # Affichage des statistiques principales du joueur

Cette fonction génère une page de statistiques affichant le nombre total de chocolatines, le CPS généré automatiquement, le nombre de clics effectués, et le temps total de jeu. 
5. Gestion des bâtiments (builds)

def build_cost(build):
    # le coût d'un build augmente de 15% à chaque achat
    return round(build["cost"] * (1.15 ** build["owned"]))

for i, build in enumerate(builds):
    rect = build_buttons_rects[i]
    if rect.collidepoint(mx, my):
        cost = build_cost(build)
        if state["count"] >= cost:
            state["count"] -= cost
            build["owned"] += 1

Chaque bâtiment génère automatiquement des chocolatines par seconde (CPS). Le coût des bâtiments augmente de 15% à chaque achat afin de créer une progression graduelle dans le jeu. Le joueur doit donc accumuler davantage de chocolatines pour débloquer des niveaux de production plus élevés.
6. Gestion des améliorations (upgrades)

def upgrade_cost(upg):
    return upg.get("cost", 0)

def apply_upgrade(upg):
    """Double le boost des builds dont le type correspond à l'upgrade."""
    t = upg.get("type")
    if not t:
        return
    for b in builds:
        if b.get("type") == t:
            b["boost"] *= 2

Les upgrades permettent d’améliorer l’efficacité des bâtiments déjà achetés. Lorsqu’une amélioration est acquise, elle double le boost de production des bâtiments d’un certain type. Cela encourage le joueur à investir non seulement dans de nouveaux bâtiments mais aussi dans l’optimisation de ceux déjà 

Le code : 
https://github.com/lina48/chocolatine-clicker- 
pour l’exécuter : python test.py 
