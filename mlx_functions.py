from typing import Any
from mlx.mlx import Mlx
import os

MAX_WINDOW_W = 2400
MAX_WINDOW_H = 1200
TEXT_ZONE_HEIGHT = 40

# --- Keycodes MAC (Touches QWERTY standard) ---
KEY_ESC_MAC = 53
KEY_R_MAC = 15   # R pour Re-generate
KEY_P_MAC = 35   # P pour Path (Show/Hide)
KEY_C_MAC = 8    # C pour Color
KEY_F_MAC = 3    # F pour Forty-Two (Pattern 42)
KEY_A_MAC = 0  # A

# --- Keycodes LINUX (X11 / ASCII Minuscule) ---
KEY_ESC_LINUX = 65307
KEY_R_LINUX = 114  # 'r'
KEY_P_LINUX = 112  # 'p'
KEY_C_LINUX = 99   # 'c'
KEY_F_LINUX = 102  # 'f'
KEY_A_LINUX = 97  # 'a'


def key_hook(keycode: int, param: Any) -> int:
    """
    Capte les événements clavier.
    Ferme proprement le programme si la touche Échap est pressée.

    Args:
        keycode (int): valeur de la touche tapée
        param (Any): le colis contenant les infos nécessaires

    Returns:
        int: 0 qui signale le succes de l'operation
    """
    # 1. Quitter (ESC)
    if keycode == KEY_ESC_MAC or keycode == KEY_ESC_LINUX:
        print("Closing the maze...")
        param["tools_mlx"].mlx_destroy_window(param["real_ptr"],
                                              param["win_ptr"])
        os._exit(0)

    # 2. Re-générer un nouveau labyrinthe (R)
    elif keycode in (KEY_R_MAC, KEY_R_LINUX):
        print("Generating new maze...")
        param["game"].regenerate_maze()
        param["game"].draw()

    # 3. Afficher/Cacher le chemin de résolution (P)
    elif keycode in (KEY_P_MAC, KEY_P_LINUX):
        print("Change solution path display...")
        param["game"].toggle_path()
        param["game"].draw()

    # 4. Changer les couleurs des murs (C)
    elif keycode in (KEY_C_MAC, KEY_C_LINUX):
        print("Changing walls color...")
        param["game"].change_colors()
        param["game"].draw()

    # 5. [Optionnel] Afficher le pattern "42" (F)
    elif keycode in (KEY_F_MAC, KEY_F_LINUX):
        print("Changing pattern 42 color...")
        param["game"].change_pattern_color()
        param["game"].draw()

    # 6. [Bonus] Affiche un pattern 'A_MAZE_ING' (A)
    elif keycode in (KEY_A_MAC, KEY_A_LINUX):
        print("Generating A_MAZE_ING pattern !")
        if not (param["game"].width < 55 or param["game"].height < 9):
            param["game"].generate_amazing()
            param["game"].draw()
        else:
            print("-> width must be >= 55 and height >= 9")

    return 0


def mlx_setup(width: int,
              height: int,
              game_instance: Any) -> tuple[Any, Any, Any, int]:
    """
    Initialise l'outil MiniLibX (MLX).

    Args:
        width (int): la largeur du cadre.
        height (int): la hauteur du cadre.
        game_instance (Any): l'instance principale du jeu (qui gere l'etat).

    Returns:
        tuple[Any, Any, Any, int]: Un ensemble contenant :
            - tools_mlx: la boite contenant les outils mlx.
            - real_ptr: le ticket de connexion à la MLX.
            - win_ptr: l'identifiant de l'ecran que nous avons ouvert.
            - tile_size: la taille de chaque case calculée pour l'écran.
    """
    # 1. Calcul dynamique de la taille d'une case (TILE_SIZE)
    tile_w = MAX_WINDOW_W // width
    tile_h = MAX_WINDOW_H // height
    tile_size = min(tile_w, tile_h)
    # Petite sécurité : si le labyrinthe est absurdement grand,
    # on garde au moins 1 pixel par case
    if tile_size < 2:
        tile_size = 2
    # on initialise Mlx en tools_mlx
    tools_mlx = Mlx()
    real_ptr = tools_mlx.mlx_init()
    # 2. Calcul des dimensions finales de la fenêtre en PIXELS
    pixel_width = width * tile_size
    pixel_height = (height * tile_size) + TEXT_ZONE_HEIGHT
    # 3. Appel aux fonctions de votre bibliothèque MLX
    win_ptr = tools_mlx.mlx_new_window(real_ptr,
                                       pixel_width,
                                       pixel_height,
                                       "'A-Maze-ing 42' by jfoeller//yafranco")
    # Création du "param" (le colis contenant les infos pour le hook)
    param: dict[str, Any] = {
        "tools_mlx": tools_mlx,
        "real_ptr": real_ptr,
        "win_ptr": win_ptr,
        "game": game_instance
    }

    # 4. Enregistrement des Hooks
    tools_mlx.mlx_key_hook(win_ptr, key_hook, param)
    # Force la MLX à appeler la fonction de dessin en continu
    tools_mlx.mlx_loop_hook(real_ptr, game_instance.draw, None)

    return (tools_mlx, real_ptr, win_ptr, tile_size)
