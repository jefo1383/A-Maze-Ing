from typing import List, Any


def get_path_str(path: List[tuple[int, int]]) -> str:
    """
    Convertit un chemin de coordonnées en une chaîne de directions.
    Parcourt la liste des coordonnées (x, y) représentant la solution du
    labyrinthe et calcule le delta (dx, dy) entre chaque étape consécutive.
    Transforme ces mouvements mathématiques en lettres cardinales (N, S, E, W)
    pour générer la chaîne de solution requise par le format d'export.

    Args:
        path (List[tuple[int, int]]): La liste ordonnée des coordonnées du
        chemin, obtenue via solve_bfs.
        Chaque élément est un tuple (x, y).

    Returns:
        str: Une chaîne de caractères représentant la suite des mouvements
            pour aller de l'entrée à la sortie (ex: "EEESWNN"). Retourne
            une chaîne vide si le chemin contient moins de 2 points.
    """
    res: str = ""
    for i in range(len(path) - 1):
        curr = path[i]
        nxt = path[i + 1]
        dx = nxt[0] - curr[0]
        dy = nxt[1] - curr[1]
        if dx == 1:
            res += "E"
        elif dx == -1:
            res += "W"
        elif dy == 1:
            res += "S"
        elif dy == -1:
            res += "N"
    return res


def _to_hex(cell_value: int) -> str:
    """
    Convertit une valeur entière (0-15)
    en caractère hexadécimal majuscule.

    Args:
        cell_value (int): la valeur de la cellule en entier.

    Returns:
        str: la valeur de la cellule,
        un caractère hexadécimal unique (0-9, A-F).
    """
    # on retourne la valeur Hexadecimal de cell_value
    return f"{cell_value:X}"


def export_to_file(grid: list[list[Any]],
                   start: tuple[int, int],
                   end: tuple[int, int],
                   path_solution: str,
                   filename: str) -> None:
    """
    Exporte les données du labyrinthe

    Args:
        grid (list[list[Any]]): la grille du labytrinthe,
        Any represente les objets 'Cell'.
        start (tuple[int, int]):la case correspondant au départ du labyrinthe.
        end (tuple[int, int]): la case correspondant a l'arrivée du labyrinthe.
        path_solution (str): suite de caractères (ex: 'NSSW')
        représentant la solution.
        filename (str): nom du fichier sur lequel enregistrer les données.

    Returns:
        None : rien, la fonction crée juste un fichier.
    """
    with open(filename, "w") as file:
        # 1. Le labyrinthe
        for row in grid:
            for cell in row:
                file.write(_to_hex(cell.walls))

            # 2. Un retour a la ligne
            file.write("\n")

        # 3. Une ligne vide
        file.write("\n")

        # 4. Les coordonnées d'entrée (x y)
        file.write(f"{start[0]},{start[1]}\n")

        # 5. Les coordonnées de sortie (x y)
        file.write(f"{end[0]},{end[1]}\n")

        # 6. Le chemin de résolution
        file.write(f"{path_solution}\n")
