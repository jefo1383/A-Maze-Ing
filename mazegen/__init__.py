from random import randrange, choice, seed
from typing import Any, Optional, List, Dict
from collections import deque


class MazeGenerator:
    """
    Générateur de labyrinthes (MazeGenerator) utilisant l'algorithme de Prim.

    Exemple d'utilisation :
    ----------------------
    from mazegen import MazeGenerator

    # 1. Instanciation avec paramètres personnalisés
    # (largeur, hauteur, labyrinthe parfait, point d'entrée,
    # point de sortie, seed optionnelle)
    maze = MazeGenerator(width=20, height=15, perfect=True, entry=(0, 0),
    exit=(19,14), custom_seed=42)

    # 2. Génération et accès a la structure
    # (retourne une grille 2D d'objets _Cell)
    maze._embed_42_pattern
    grid = maze.generate_prim()

    # 3. Accès à la solution
    # Calcule le chemin le plus court entre l'entrée et la sortie
    solution_path = maze.solve_bfs(grid, start=(0, 0), end=(19, 14))
    """

    N, E, S, W = 1, 2, 4, 8

    class _Cell:
        '''
        Objet cellule representant une case du labyrinthe.
        Permet une memoire persistante pour les murs presents
        sur la case (.walls), le flag de detection du pattern
        (.mask_42) et le flag d'une case deja visitee pour
        la generation du labyrinthe (.visited)
        '''
        def __init__(self) -> None:
            self.walls: int = 15
            self.mask_42: bool = False
            self.visited: bool = False

    def __init__(self, width: int, height: int, perfect: bool,
                 entry: tuple[int, int], exit: tuple[int, int],
                 custom_seed: Optional[int] = None) -> None:
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Error: ENTRY out of bounds.")
        if not (0 <= exit[0] < width and 0 <= exit[1] < height):
            raise ValueError("Error: EXIT out of bounds.")
        self.width = width
        self.height = height
        self.perfect = perfect
        self.entry = entry
        self.exit = exit
        if custom_seed:
            self.custom_seed = custom_seed
            seed(custom_seed)
        self.grid: list[list[MazeGenerator._Cell]] =\
            [[self._Cell() for _ in range(width)] for _ in range(height)]

    def _remove_wall(self, x1: int, y1: int, x2: int, y2: int) -> None:
        '''
        Enleve les murs mitoyens entre deux cellules.
        Args: x1, y1 -> les coordonnees de la 1ere cellule.
              x2, y2 -> les coordonnees de la 2eme cellule.
        '''
        if x2 > x1:
            self.grid[y1][x1].walls &= ~self.E
            self.grid[y2][x2].walls &= ~self.W
        elif x2 < x1:
            self.grid[y1][x1].walls &= ~self.W
            self.grid[y2][x2].walls &= ~self.E
        if y2 > y1:
            self.grid[y1][x1].walls &= ~self.S
            self.grid[y2][x2].walls &= ~self.N
        elif y2 < y1:
            self.grid[y1][x1].walls &= ~self.N
            self.grid[y2][x2].walls &= ~self.S

    def _embed_42_pattern(self) -> bool:
        '''
        Verifie que l'entree et la sortie ne soient pas sur le pattern
        puis applique un masque via les flags pour exclure ces cases
        du labyrinthe.
        Retour:
            Un booleen vrai ou faux pour savoir si la generation du
            labyrinthe est possible.
        '''
        pattern = [
            "   # ###",
            "  #    #",
            " #   ###",
            "#### #  ",
            "   # ###",
            "   #    "
        ]
        p_w, p_h = len(pattern[0]), len(pattern)
        start_x = (self.width // 2) - (p_w // 2)
        start_y = (self.height // 2) - (p_h // 2)

        # Vérification de l'entree et la sortie
        for pt in [self.entry, self.exit]:
            px, py = pt
            if start_x <= px < start_x + p_w and start_y <= py < start_y + p_h:
                if pattern[py - start_y][px - start_x] == "#":
                    print(f"CRITICAL ERROR: {pt} collides with 42 pattern.")
                    return False

        for y, line in enumerate(pattern):
            for x, c in enumerate(line):
                if c == "#":
                    self.grid[start_y + y][start_x + x].mask_42 = True
                    self.grid[start_y + y][start_x + x].visited = True
        return True

    def _embed_amazing_pattern(self) -> bool:
        '''
        Verifie que l'entree et la sortie ne soient pas sur le pattern
        bonus puis applique un masque via les flags pour exclure ces cases
        du labyrinthe.
        Retour:
            Un booleen vrai ou faux pour savoir si la generation du
            labyrinthe est possible.
        '''
        pattern = [
            " #        #   #  #   #### ####      ### #   #  ### ",
            "#  #      ## ## #  #    # #          #  ##  # #    ",
            "#### #### # # # ####   #  ###  ####  #  # # # # ###",
            "#  #      #   # #  #  #   #          #  #  ## #   #",
            "#  #      #   # #  # #### ####      ### #   #  ### "
        ]
        center_x: int = self.width // 2
        center_y: int = self.height // 2
        start_x: int = center_x - (len(pattern[0]) // 2)
        start_y: int = center_y - (len(pattern) // 2)
        # Calcul de la zone du pattern ---
        end_x = start_x + len(pattern[0])
        end_y = start_y + len(pattern)

        # Vérification des collisions avec l'entrée et la sortie
        entry_in_box = (start_x <= self.entry[0] < end_x) and (
            start_y <= self.entry[1] < end_y)
        exit_in_box = (start_x <= self.exit[0] < end_x) and (
            start_y <= self.exit[1] < end_y)

        if entry_in_box or exit_in_box:
            print(" -> Entry or exit in new pattern")
            return False
        for y, line in enumerate(pattern):
            for x, c in enumerate(line):
                if c == "#":
                    self.grid[start_y + y][start_x + x].mask_42 = True
                    self.grid[start_y + y][start_x + x].visited = True
        return True

    def _get_frontier(self: Any,
                      position: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Scanne les 4 directions autour d'une position donnée et retourne
        une liste des coordonnées des cases voisines qui n'ont pas encore
        été visitées.

        Args:
            self: L'instance actuelle de la classe Maze.
            position (tuple[int, int]): la position de la case actuelle,
            point de depart de la recherche.
        Returns:
            list[tuple[int, int]]: Une liste de coordonnées (x,y)
            correspondant aux voisins non visités.
            Chaque tuple est au format (x, y).
        """
        # On recupere la position.
        cx, cy = position
        valid_neighbors: list[tuple[int, int]] = []
        # On instancie les differents mouvements possible: N, E, S et O.
        neighbor_cases: list[tuple[int, int]] =\
            [(0, 1), (0, -1), (1, 0), (-1, 0)]
        # On parcourt les cases voisines
        for case in neighbor_cases:
            dx, dy = case
            nx = cx + dx
            ny = cy + dy
            # On verifie la validite de la case voisine.
            if (0 <= nx < self.width) and (0 <= ny < self.height):
                if not self.grid[ny][nx].visited:
                    # on l'ajoute a la liste des cases voisines valides.
                    valid_neighbors.append((nx, ny))
        # On retourne la liste des cases voisines valides.
        return valid_neighbors

    def generate_prim(self) -> List[List[_Cell]]:
        '''
        Génère le labyrinthe en utilisant l'algorithme de Prim randomisé.
        Peut produire un labyrinthe "parfait" (un seul chemin possible
        entre deux points) ou "imparfait" (avec des boucles et
        chemins multiples) selon la configuration.

        Args:
            self: L'instance actuelle de la classe Maze.

        Returns:
            None : le labyrinthe est généré directement dans
            l'attribut self.grid.
        '''
        # La "frontière" contient les murs adjacents aux cases déjà visitées.
        # Format : ((x_source, y_source), (x_dest, y_dest))
        frontier: list[tuple[tuple[int, int], tuple[int, int]]] = []
        # Vecteurs de direction pour explorer les voisins :
        # Sud, Nord, Est, Ouest
        neighbor_cases: list[tuple[int, int]] = [(0, 1),
                                                 (0, -1),
                                                 (1, 0),
                                                 (-1, 0)]
        # --- 1. Initialisation ---
        cx, cy = self.entry
        self.grid[cy][cx].visited = True
        # On peuple la frontière initiale avec les voisins de la case de départ
        valid_neighbors: list[tuple[int, int]] = self._get_frontier((cx, cy))
        for neighbor in valid_neighbors:
            frontier.append(((cx, cy), neighbor))
        # --- 2. Boucle principale de Prim ---
        while frontier:
            # Sélection aléatoire d'un mur dans la frontière pour
            # garantir un tracé organique
            index: int = randrange(len(frontier))
            (s_coords, d_coords) = frontier.pop(index)
            sx, sy = s_coords
            dest_x, dest_y = d_coords
            # Si la case de destination n'a pas encore été explorée,
            # on l'intègre au labyrinthe
            if not self.grid[dest_y][dest_x].visited:
                self.grid[dest_y][dest_x].visited = True
                # On ouvre le passage en cassant le mur entre la source
                # et la destination
                self._remove_wall(sx, sy, dest_x, dest_y)
                # On ajoute les nouveaux voisins découverts à la frontière
                new_neighbors = self._get_frontier(d_coords)
                for neighbor in new_neighbors:
                    frontier.append((d_coords, neighbor))
        # --- 3. Gestion des labyrinthes imparfaits ---
        # Pour rendre le labyrinthe "imparfait", on détruit aléatoirement
        # 5% des murs supplémentaires, ce qui va créer des boucles et des
        # chemins alternatifs.
        if not self.perfect:
            walls_to_break: int = int(((self.width * self.height) / 100) * 6)
            for _ in range(walls_to_break):
                # On cible une case au hasard
                x_tobreak = randrange(self.width)
                y_tobreak = randrange(self.height)
                # On choisit une direction au hasard depuis cette case
                if not self.grid[y_tobreak][x_tobreak].mask_42:
                    dx, dy = choice(neighbor_cases)
                    new_x = x_tobreak + dx
                    new_y = y_tobreak + dy
                    # Si la case voisine est dans les limites de la grille,
                    # on casse le mur
                    if (0 <= new_x < self.width) and (
                            0 <= new_y < self.height):
                        if not self.grid[new_y][new_x].mask_42:
                            self._remove_wall(x_tobreak, y_tobreak,
                                              new_x, new_y)
        return self.grid

    def solve_bfs(self) -> List[tuple[int, int]]:
        '''
        Algorithme Breadth-First Search de generation du chemin le plus
        court entre l'entree et la sortie du labyrinthe.
        Args:
        Utilise le self pour acceder aux donnees du labyrinthe.
        Return:
        Retourne la liste des coordonees du chemin de l'entree vers
        la sortie.
        '''
        queue: deque[tuple[int, int]] = deque([self.entry])
        parent: Dict[tuple[int, int], Optional[tuple[int, int]]] =\
            {self.entry: None}
        found_cell: Optional[tuple[int, int]] = None

        while queue:
            current_cell = queue.popleft()
            if current_cell == self.exit:
                found_cell = current_cell
                break
            cx, cy = current_cell
            directions: List[tuple[int, int, int]] = [(1, 0, -1), (2, 1, 0),
                                                      (4, 0, 1), (8, -1, 0)]
            for mask, dx, dy in directions:
                if not (self.grid[cy][cx].walls & mask):
                    nx, ny = cx + dx, cy + dy
                    neighbor: tuple[int, int] = (nx, ny)
                    if neighbor not in parent:
                        queue.append(neighbor)
                        parent[neighbor] = current_cell
        if found_cell is None or found_cell != self.exit:
            raise ValueError("Exit not found")
        path: List[tuple[int, int]] = []
        curr: Optional[tuple[int, int]] = found_cell
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        return path[::-1]
