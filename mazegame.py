from typing import Any
from utils import get_path_str, export_to_file
from mazegen import MazeGenerator
import random


class MazeGame:
    '''
    Classe generale qui va instancier le generateur de labyrinthes,
    gerer l'affichage graphique via Mlx, le calcul du chemin,
    et l'export.
    '''
    def __init__(self, width: int, height: int, perfect: bool = True,
                 entry: tuple[int, int] = (0, 0), exit: tuple[int, int] =
                 (0, 0), output_file: str = "default.txt") -> None:
        self.width = width
        self.height = height
        self.perfect = perfect
        self.start = entry
        self.end = exit
        self.output_file = output_file
        self.needs_update = True
        self.is_valid = True

        # L'État Visuel (Initialisé en premier pour éviter les crashs)
        self.show_path = False
        self.wall_color = 0xFFFFFF
        self.pattern_color = 0x00FF00
        self.mlx = None
        self.real_ptr = None
        self.win_ptr = None
        self.tile_size = 0

        # Le Moteur
        self.generator = MazeGenerator(width, height, perfect, self.start,
                                       self.end)
        # Tentative d'insertion du pattern obligatoire
        if not (self.width < 12 or self.height < 10):
            if not self.generator._embed_42_pattern():
                self.is_valid = False
                return
        # Generation du labyrinthe
        self.generator.generate_prim()

        # Calcul du chemin
        self.solution_path = self.generator.solve_bfs()

        # Export
        solution_str = get_path_str(self.solution_path)
        export_to_file(self.generator.grid, self.start, self.end, solution_str,
                       output_file)

        # L'État Visuel
        self.show_path = False
        self.wall_color = 0xFFFFFF
        self.pattern_color = 0x00FF00

        # Données MLX
        self.mlx = None
        self.real_ptr = None
        self.win_ptr = None
        self.tile_size = 0

    def set_mlx_data(self, tools: Any, real: Any, win: Any, tile: int) -> None:
        """Injecte les pointeurs de la fenêtre dans le jeu."""
        self.mlx = tools
        self.real_ptr = real
        self.win_ptr = win
        self.tile_size = tile

    # ==========================================
    #   (Dev A) : Le Dessin
    # ==========================================

    def _put_pixel_img(self,
                       buffer: memoryview,
                       x: int,
                       y: int,
                       color: int,
                       line_bytes: int,
                       max_w: int,
                       max_h: int) -> None:
        """
        Modifie la mémoire RAM de l'image directement pour un pixel donné.
        Args:
            buffer (memoryview): La vue mémoire 1D représentant l'image MLX.
            x (int): La coordonnée X du pixel à modifier.
            y (int): La coordonnée Y du pixel à modifier.
            color (int): La couleur du pixel au format hexadécimal.
            line_bytes (int): La taille en octets d'une ligne complète
            de l'image.
            max_w (int): La largeur maximale de l'image en pixels.
            max_h (int): La hauteur maximale de l'image en pixels.
        Returns:
            None
        """
        # Sécurité : on ne dessine pas en dehors de l'image
        # pour ne pas faire crasher la mémoire
        if 0 <= x < max_w and 0 <= y < max_h:
            # Calcul de l'emplacement exact du pixel
            # dans le tableau 1D de la mémoire
            index = (y * line_bytes) + (x * 4)

            # Découpage de la couleur Hexadécimale (0xRRGGBB) en octets
            buffer[index] = color & 0xFF             # Bleu
            buffer[index + 1] = (color >> 8) & 0xFF  # Vert
            buffer[index + 2] = (color >> 16) & 0xFF  # Rouge
            buffer[index + 3] = 255

    def draw(self, *args: Any) -> None:
        """
        Dessine la grille en utilisant le Double Buffering.
        Cette méthode est responsable du rendu complet du jeu. Elle construit
        une nouvelle image en mémoire contenant les cellules, les murs,
        les motifs spéciaux, le chemin de résolution et la légende interactive.
        Une fois l'image terminée, elle est envoyée à la fenêtre MLX et
        l'ancienne image est détruite pour libérer la RAM et
        éviter les scintillements.
        Args:
            *args (Any): Arguments positionnels variables (principalement pour
                absorber les arguments par défaut envoyés par les hooks
                de la MLX lors des événements de rafraîchissement).
        Returns:
            None
        """
        if not self.mlx or not getattr(self, 'needs_update', True):
            return
        if not self.is_valid:
            # On affiche un message d'erreur à l'écran via MLX
            self.mlx.mlx_string_put(self.real_ptr, self.win_ptr, 50, 50,
                                    0xFF0000, "ERROR: ENTRY/EXIT IN PATTERN")
            return

        pixel_w = self.width * self.tile_size
        pixel_h = self.height * self.tile_size

        # 1. On détruit l'ANCIENNE image s'il y en a une, pour libérer la RAM
        if hasattr(self, 'current_img') and getattr(self, 'current_img', None):
            self.mlx.mlx_destroy_image(self.real_ptr, self.current_img)

        # 2. Création de la NOUVELLE image vierge
        img_ptr = self.mlx.mlx_new_image(self.real_ptr, pixel_w, pixel_h)
        img_data = self.mlx.mlx_get_data_addr(img_ptr)

        buffer = img_data[0]
        line_bytes = img_data[2]

        grid = self.generator.grid
        t_size = self.tile_size

        # 3. On peint dans la RAM
        thickness = 2
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                px = x * t_size
                py = y * t_size
                value = cell.walls

                # Arrière-plan des cases
                # (optionnel mais utile pour éviter le noir total)
                for dy in range(t_size):
                    for dx in range(t_size):
                        self._put_pixel_img(buffer,
                                            px + dx,
                                            py + dy,
                                            0x111111,
                                            line_bytes,
                                            pixel_w,
                                            pixel_h)

                # Les Murs
                # Mur NORD
                if value & 1:
                    for t in range(thickness):  # On répète le dessin 't' fois
                        for i in range(t_size):
                            self._put_pixel_img(buffer,
                                                px + i,
                                                py + t,
                                                self.wall_color,
                                                line_bytes,
                                                pixel_w,
                                                pixel_h)
                # Mur EST
                if value & 2:
                    for t in range(thickness):
                        for i in range(t_size):
                            # On décale vers l'intérieur (px + t_size - 1 - t)
                            self._put_pixel_img(buffer,
                                                px + t_size - 1 - t,
                                                py + i,
                                                self.wall_color,
                                                line_bytes,
                                                pixel_w,
                                                pixel_h)
                # Mur SUD
                if value & 4:
                    for t in range(thickness):
                        for i in range(t_size):
                            # On décale vers l'intérieur (py + t_size - 1 - t)
                            self._put_pixel_img(buffer,
                                                px + i,
                                                py + t_size - 1 - t,
                                                self.wall_color,
                                                line_bytes,
                                                pixel_w,
                                                pixel_h)
                # Mur OUEST
                if value & 8:
                    for t in range(thickness):
                        for i in range(t_size):
                            self._put_pixel_img(buffer,
                                                px + t,
                                                py + i,
                                                self.wall_color,
                                                line_bytes,
                                                pixel_w,
                                                pixel_h)

                # Le Pattern
                if cell.mask_42:
                    for dy in range(1, t_size):
                        for dx in range(1, t_size):
                            self._put_pixel_img(buffer,
                                                px + dx,
                                                py + dy,
                                                self.pattern_color,
                                                line_bytes,
                                                pixel_w,
                                                pixel_h)

                # Départ et Arrivée
                if (x, y) == self.start:
                    for dy in range(1, t_size):
                        for dx in range(1, t_size):
                            self._put_pixel_img(buffer,
                                                px + dx,
                                                py + dy,
                                                0x00FF00,
                                                line_bytes,
                                                pixel_w,
                                                pixel_h)
                elif (x, y) == self.end:
                    for dy in range(1, t_size):
                        for dx in range(1, t_size):
                            self._put_pixel_img(buffer,
                                                px + dx,
                                                py + dy,
                                                0xFF0000,
                                                line_bytes,
                                                pixel_w,
                                                pixel_h)

        # Le Chemin
        if self.show_path and self.solution_path:
            for cx, cy in self.solution_path:
                px = cx * t_size
                py = cy * t_size
                for dy in range(2, t_size - 1):
                    for dx in range(2, t_size - 1):
                        self._put_pixel_img(buffer,
                                            px + dx,
                                            py + dy,
                                            0x0000FF,
                                            line_bytes,
                                            pixel_w,
                                            pixel_h)

        # 4. On envoie l'image à la fenêtre
        self.mlx.mlx_put_image_to_window(self.real_ptr,
                                         self.win_ptr,
                                         img_ptr,
                                         0,
                                         0)

        # 5. Ajout de la legende
        text_y = pixel_h + 10
        # On définit les segments de notre barre de commandes
        commands = [
            "[R]=Regen",
            "[P]=Path",
            "[C]=Walls",
            "[F]=Pattern",
            "[A]=A_MAZE_ING",
            "[ESC]=Exit"
        ]
        space_between = 20
        pixels_per_char = 10
        total_txt_width = 0
        for cmd in commands:
            total_txt_width += (len(cmd) * pixels_per_char) + space_between
        # On retire le dernier espace en trop à la fin
        total_txt_width -= space_between
        # 3. On calcule le X de départ pour que l'ensemble soit centré
        start_x = (pixel_w - total_txt_width) // 2
        # Sécurité : si la fenêtre est trop petite, on commence à 10px
        if start_x < 10:
            start_x = 10
        # 4. Affichage
        try:
            current_x = start_x
            for cmd in commands:
                self.mlx.mlx_string_put(self.real_ptr, self.win_ptr,
                                        current_x, text_y, 0xFFFFFF, cmd)
                # On décale pour le mot suivant
                current_x += (len(cmd) * pixels_per_char) + space_between
        except Exception as e:
            print(f" -> Display caption error : {e}")

        # 6. On force Linux à lire la mémoire
        try:
            self.mlx.mlx_do_sync(self.real_ptr)
        except Exception:
            pass

        # 7. On sauvegarde l'image
        self.current_img = img_ptr

        self.needs_update = False

    # ==========================================
    #   ACTIONS CLAVIER (Dev B)
    # ==========================================

    def regenerate_maze(self) -> None:
        '''
        Régénère un nouveau labyrinthe avec le motif obligatoire '42'.

        Instancie un nouveau MazeGenerator pour réinitialiser la grille. Si les
        dimensions le permettent (min 12x10), tente d'insérer le motif '42' au
        centre. En cas de collision avec l'entrée ou la sortie, le labyrinthe
        est invalidé pour déclencher l'affichage de l'erreur. Sinon, le
        labyrinthe est généré (Prim), résolu (BFS), exporté dans le
        fichier texte, et l'affichage est mis à jour.
        '''
        self.generator = MazeGenerator(self.width, self.height, self.perfect,
                                       self.start, self.end)
        if not (self.width < 12 or self.height < 10):
            if not self.generator._embed_42_pattern():
                self.is_valid = False
                self.needs_update = True
                return
        self.is_valid = True
        self.generator.generate_prim()
        self.solution_path = self.generator.solve_bfs()
        solution_str = get_path_str(self.solution_path)
        export_to_file(self.generator.grid,
                       self.start,
                       self.end,
                       solution_str,
                       self.output_file)
        self.show_path = False
        self.needs_update = True
        print(" -> Maze drawn !")

    def generate_amazing(self) -> None:
        '''
        Génère un nouveau labyrinthe avec le motif bonus 'A_MAZE_ING'.

        Fonctionne de manière similaire à regenerate_maze(), mais tente
        d'insérer le motif personnalisé et étendu 'A_MAZE_ING'. Ce motif n'est
        inséré que si la grille fait au moins 55x9. Bloque la génération
        et déclenche un affichage d'erreur en cas de collision avec les
        points de départ ou d'arrivée.
        '''
        self.generator = MazeGenerator(self.width, self.height, self.perfect,
                                       self.start, self.end)
        if not (self.width < 55 or self.height < 9):
            if not self.generator._embed_amazing_pattern():
                self.is_valid = False
                self.needs_update = True
                return
        self.is_valid = True
        self.generator.generate_prim()
        self.solution_path = self.generator.solve_bfs()
        solution_str = get_path_str(self.solution_path)
        export_to_file(self.generator.grid, self.start, self.end,
                       solution_str, self.output_file)
        self.show_path = False
        self.needs_update = True
        print(" -> A_MAZE_ING drawn !")

    def toggle_path(self) -> None:
        '''
        Active ou désactive l'affichage du chemin de résolution.

        Inverse l'état du booléen de visibilité du chemin (show_path) et
        signale au moteur de rendu qu'une mise à jour visuelle est nécessaire
        lors de la prochaine itération de la boucle MLX. Affiche également
        l'état actuel dans le terminal.
        '''
        self.show_path = not self.show_path
        self.needs_update = True
        print(f" -> Path {'displayed' if self.show_path else 'hidden'}.")

    def change_colors(self) -> None:
        '''
        Modifie aléatoirement la couleur des murs du labyrinthe.

        Génère une nouvelle couleur hexadécimale aléatoire pour les murs.
        La plage de génération commence à 0x222222 (et non 0x000000) afin
        d'éviter de tirer des couleurs trop sombres qui se confondraient
        avec l'arrière-plan de la fenêtre.
        '''
        self.wall_color = random.randint(0x222222, 0xFFFFFF)
        self.needs_update = True
        print(" -> New walls color applied")

    def change_pattern_color(self) -> None:
        '''
        Modifie aléatoirement la couleur du motif spécial.

        Génère une nouvelle couleur hexadécimale aléatoire pour le remplissage
        du motif '42' ou 'A_MAZE_ING'. Comme pour les murs, les couleurs trop
        sombres sont exclues pour garantir la lisibilité.
        '''
        self.pattern_color = random.randint(0x222222, 0xFFFFFF)
        self.needs_update = True
        print(" -> New 42 pattern color applied")
