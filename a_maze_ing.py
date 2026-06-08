import sys
from mlx.mlx import Mlx
from typing import Dict, Any
import random
from mazegame import MazeGame
from mlx_functions import mlx_setup
from pathlib import Path


def handle_args() -> str:
    '''
    Validation des arguments entree en ligne de commande.
    Return:
    Retourne une string avec le nom du fichier de configuration.
    '''
    if len(sys.argv) != 2 or ".txt" not in sys.argv[1]:
        print("Args requirement: python3 a_maze_ing.py <config.txt>")
        sys.exit(1)
    return sys.argv[1]


def parse_config(file_path: str) -> dict[str, Any]:
    """
    Lit un fichier de configuration et retourne
    un dictionnaire de paires clé-valeur.

    Args:
        file_path (str): Le chemin vers le fichier de configuration.

    Returns:
        dict[str, Any]: Un dictionnaire contenant les configurations.

    Raises:
        FileNotFoundError: Si le fichier spécifié n'existe pas.
        ValueError: Si une ligne est mal formatée (pas de '=').
        RuntimeError: Pour toute autre erreur inattendue.
    """
    config_data: dict[str, Any] = {}
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            for line_number, line in enumerate(file, 1):
                clean_line = line.strip()
                if not clean_line or clean_line.startswith("#"):
                    continue
                if '=' not in clean_line:
                    print(f"Syntax error on line {line_number}: "
                          f"{clean_line} (required: KEY=VALUE)")
                    sys.exit(1)
                key, value = clean_line.split('=', 1)
                config_data[key.strip()] = value.strip()
    except FileNotFoundError:
        raise FileNotFoundError("Error : setup file "
                                f"'{file_path}' is not found.")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while reading the file: {e}")
    return config_data


def validate_data(config_data: dict[str, Any]) -> bool:
    '''
    Valide, nettoie et convertit les types de données.
    Attention : cette fonction modifie le dictionnaire
    config_data en place pour convertir les valeurs.

    Args:
        config_data (dict[str, Any]): Dictionnaire de configuration
        (doit contenir WIDTH, HEIGHT, ENTRY, etc.):
            - WIDTH: La largeur de la grille du labyrinthe
            (doit être un entier positif).
            - HEIGHT: La hauteur de la grille du labyrinthe
            (doit être un entier positif).
            - ENTRY: Les coordonnees (chaine de caracteres(str)
            au format "x, y") de la case de depart du labyrinthe.
            - EXIT: Les coordonnees (chaine de caracteres(str)
            au format "x, y") de la case d'arrivee du labyrinthe.
            - OUTPUT_FILE: Le nom ou le chemin du fichier
            où le labyrinthe sera sauvegardé.
            - PERFECT: Une chaîne "true" ou "false"
            indiquant la perfection du tracé.

    Returns:
        bool: Résultat de la validation.
            - True : Si toutes les clés sont valides et converties.
            - False : Si une clé manque ou si un format est incorrect.
    '''
    required_keys = ["WIDTH",
                     "HEIGHT",
                     "ENTRY",
                     "EXIT",
                     "OUTPUT_FILE",
                     "PERFECT"]
    # On verifie que toutes les cles sont bien dans config_data.
    for key in required_keys:
        if key not in config_data:
            print(f"Error: {key} is missing from config_data file.")
            return False
    # On verifie que toutes les cles ont des donnees valides.
    try:
        # On verifie que la hauteur et la largeur sont bien des entiers.
        config_data["WIDTH"] = int(config_data["WIDTH"])
        config_data["HEIGHT"] = int(config_data["HEIGHT"])
        # On verifie que la hauteur
        # et la largeur sont bien des entiers positifs.
        if config_data["WIDTH"] <= 0 or config_data["HEIGHT"] <= 0:
            print("Error: 'Width' and 'Height' "
                  "must be positive values, above 0")
            return False
        # On recupere les coordonnees d'entree.
        entry_parts = config_data["ENTRY"].split(',')
        # On verifie que les donnees sont au bon format.
        if len(entry_parts) != 2:
            print("Error : ENTRY format must be 'x,y'.")
            return False
        config_data["ENTRY"] = (int(entry_parts[0].strip()),
                                int(entry_parts[1].strip()))
        # On recupere les coordonnees de sortie.
        exit_parts = config_data["EXIT"].split(',')
        # On verifie que les donnees sont au bon format.
        if len(exit_parts) != 2:
            print("Error : EXIT format must be 'x,y'.")
            return False
        config_data["EXIT"] = (int(exit_parts[0].strip()),
                               int(exit_parts[1].strip()))
        # On verifie que le depart et l'arrivee ne sont pas identiques.
        if config_data["ENTRY"] == config_data["EXIT"]:
            print("Error : ENTRY & EXIT can't have the same coordinates.")
            return False
        # On verifie que le nom du fichier d'output est present.
        output_file = str(config_data["OUTPUT_FILE"]).strip()
        if not output_file:
            print("Error: OUTPUT_FILE cannot be empty.")
            return False
        # On verifie que le nom du fichier d'output est valide.
        path = Path(output_file)
        if path.suffix != '.txt':
            print(f"Error: OUTPUT_FILE '{output_file}' must end with '.txt'.")
            return False
        # On recupere la clef PERFECT.
        perfect_str = str(config_data["PERFECT"]).strip().lower()
        # On verifie la valeur de PERFECT
        if perfect_str == "true":
            config_data["PERFECT"] = True
        elif perfect_str == "false":
            config_data["PERFECT"] = False
        else:
            print("Error: Key 'PERFECT' must be 'True' or 'False'")
            return False
    except ValueError as e:
        print(f"Error: {e}")
        return False
    # Si tout est ok, on valide les donnees.
    return True


def main() -> None:
    '''
    Point d'entree du programme.
    Recupere les arguments, les traite et initialise une fenetre
    avec un premier labyrinthe.
    '''
    try:
        config: Dict[str, Any] = parse_config(handle_args())
        if validate_data(config):
            if "SEED" in config:
                random.seed(config["SEED"])
            game = MazeGame(config["WIDTH"],
                            config["HEIGHT"],
                            config["PERFECT"],
                            config["ENTRY"],
                            config["EXIT"],
                            config["OUTPUT_FILE"])
            tools: Mlx
            tools, real, win, tile = mlx_setup(config["WIDTH"],
                                               config["HEIGHT"],
                                               game)
            # 3. On injecte les pointeurs de la fenêtre dans la classe
            game.set_mlx_data(tools, real, win, tile)

            # 4. On dessine la première frame
            game.draw()

            print("Maze generated ! Commands:\nR = regenerate a maze\nP = "
                  "display shortest path\nC = change walls color\nF = change "
                  "42 pattern color\nA = bonus A_MAZE_ING pattern\nESC = exit")

            # 5. On lance la boucle infinie qui va écouter le clavier
            tools.mlx_loop(real)
    except (FileNotFoundError, Exception) as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
