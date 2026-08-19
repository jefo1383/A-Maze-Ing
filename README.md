_This activity has been created as part of the 42 curriculum by jfoeller and yafranco._

# 🌀 A_Maze_ing

https://github.com/user-attachments/assets/ec68d520-8a26-42c4-b892-f26ec36d4f80

Un générateur et solveur de labyrinthes interactif en Python, utilisant la **MiniLibX**. 
Ce projet a été réalisé en binôme dans le cadre du cursus 42, avec une séparation stricte des responsabilités entre la génération/infrastructure (Dev B) et le rendu visuel/pathfinding (Dev A).

---

## 🚀 Fonctionnalités Globales

- Génération de labyrinthes "Parfaits" (un seul chemin) et "Imparfaits" (boucles multiples).
- Export des données au format hexadécimal strict.
- Interface graphique propulsée par un wrapper Python de la MiniLibX.
- Résolution algorithmique intégrée avec affichage en temps réel du chemin optimal.

---

## 🛠️ Architecture et Répartition des Tâches

### 🧠 Moteur, Export et Infrastructure

Cette partie du projet se concentre sur les fondations algorithmiques et l'interfaçage système.

* **Algorithme de Génération (Prim) :**
    * **Justification du choix :** 
    L'algorithme de Prim (version randomisée) a été sélectionné pour sa stabilité et l'esthétique de ses tracés. Implémenté de manière itérative, il offre une excellente gestion de la mémoire et prévient les erreurs de dépassement de pile (*stack overflow*) inhérentes aux méthodes récursives sur de grandes grilles. 
    De plus, il génère des structures organiques avec un fort taux d'embranchements et de culs-de-sac, augmentant significativement la complexité de résolution.
    * Implémentation de l'algorithme de Prim randomisé pour assurer des tracés organiques.
    * Gestion dynamique de la "frontière" des murs.
    * Algorithme d'altération post-génération pour détruire 6% des murs et créer des labyrinthes imparfaits.
* **Export :**
    * Traduction de la grille en code hexadécimal.
    * Formatage d'écriture très strict respectant le PDF du sujet (séparateurs de lignes, coordonnées de départ/arrivée).
* **Infrastructure MiniLibX (Python/C Binding) :**
    * Mise en place d'un setup MLX orienté objet.
    * Gestion avancée des pointeurs C (`ctypes.c_void_p`) pour la communication entre Python et la bibliothèque compilée en C.
    * Calcul dynamique de la taille des cases (`tile_size`) selon la résolution maximale de l'écran.
    * Implémentation des *hooks* clavier avec fermeture propre via `os._exit(0)` pour éviter les fuites de mémoire et les exceptions systèmes.
* **Sécurité et Typage :** Code 100% validé par `mypy` (Typage strict de toutes les fonctions et structures de données).

---

## 📦 Package et Réutilisabilité (Module `mazegen`)

* **Installation :**
    * `pip install mazegen-1.0.0-py3-none-any.whl` pour une installation independante.
    * `make install` dans le cadre du projet A_MAZE_ING.
* **Utilisation :**

    Exemple d'utilisation :

    `from mazegen import MazeGenerator`

    1. Instanciation avec paramètres personnalisés
    (largeur, hauteur, labyrinthe parfait, point d'entrée,
    point de sortie, seed optionnelle)
        * `maze = MazeGenerator(width=20, height=15, perfect=True, entry=(0, 0),
    exit=(19,14), custom_seed=42)`

    2. Génération et accès a la structure
    (retourne une grille 2D d'objets _Cell)
        * `maze._embed_42_pattern`
        * `grid = maze.generate_prim()`

    3. Accès à la solution
    Calcule le chemin le plus court entre l'entrée et la sortie
        * `solution_path = maze.solve_bfs(grid, start=(0, 0), end=(19, 14))`

---

### 🎨 Rendu Visuel et Résolution

* **Rendu Graphique :**
    * Manipulation directe de la mémoire : Pour des raisons de performances, le rendu ne passe pas par des fonctions de dessin de haut niveau. L'affichage s'effectue par l'altération directe de la RAM, en modifiant le buffer de l'image pixel par pixel (gestion des octets RVB via des opérations bit à bit).
    * Double Buffering : Pour garantir la fluidité visuelle et éviter tout effet de scintillement (flickering) lors des mises à jour, une nouvelle image est générée en mémoire avant d'écraser la précédente à l'écran.
    * Décodage structurel : L'affichage dynamique des murs s'appuie sur la lecture binaire des données de chaque cellule (masques binaires pour le Nord, Sud, Est, Ouest), permettant un tracé rapide.
    * Interface Utilisateur (HUD) : Les commandes interactives sont incrustées directement dans la fenêtre MLX pour une navigation fluide.
* **Pathfinding (Résolution) :**
    * Algorithme BFS (Breadth-First Search) : Le parcours en largeur a été sélectionné pour la résolution du labyrinthe.
    * Chemin optimal garanti : Dans le cadre de la génération de labyrinthes "imparfaits" (qui comportent des murs détruits et donc des chemins multiples), le BFS assure mathématiquement de trouver la route la plus courte entre le départ et l'arrivée dans cette grille non pondérée.
    * Visualisation : Une fois la destination atteinte, l'algorithme remonte l'historique des nœuds visités pour reconstruire et afficher le tracé exact à l'écran.

---

### 🕹️ Contrôles et Utilisation

* **Contrôles :**
Une fois le labyrinthe généré et la fenêtre graphique ouverte, plusieurs commandes clavier permettent d'interagir en temps réel avec le rendu.

* **Utilisation :**
    * [R] (Regen) : Génère instantanément un nouveau labyrinthe et met à jour l'affichage.
    * [P] (Path) : Affiche ou masque le chemin de résolution optimal calculé par l'algorithme BFS.
    * [C] (Walls) : Change aléatoirement la couleur des murs.
    * [F] (Pattern 42) : Change aléatoirement la couleur du motif "42" incrusté dans la grille.
    * [A] (Pattern A_MAZE_ING) : Genere un nouveau labyrinthe avec un pattern bonus A_MAZE_ING.
    * [ESC] (Exit) : Ferme la fenêtre et quitte le programme proprement (garantissant la libération de la mémoire sans erreur système).

---

## ⚙️ Installation et Exécution

**Prérequis :** Python 3.x, wrapper MiniLibX.

Installation MiniLibX (mlx):
1. Telecharger les ressources relatives au projet A_Maze_ing
2. Renommer le fichier d'installation (.whl) mlx-2.2-py3-ubuntu-any.whl: <br>
    -> `mv mlx-2.2-py3-ubuntu-any.whl mlx-2.2-py3-none-any.whl`
3. Lancer l'intallation avec la ligne de commande suivante: <br>
    -> `python3 -m pip install mlx-2.2-py3-none-any.whl`

4. Ou via le makefile: `make install`

---

### ⚙️ Configuration et Lancement

L'exécution du générateur s'effectue en ligne de commande en lui passant un fichier de configuration spécifique en argument. 

**Syntaxe de lancement :**
`python3 a_maze_ing.py <config.txt>`

#### Le fichier de configuration
Le programme intègre un *parser* qui lit un fichier texte contenant les paramètres de génération sous la forme `CLÉ=VALEUR`. Les lignes vides ou commentées (commençant par `#`) sont ignorées.

**Paramètres requis :**

| Clé | Format attendu | Description |
| :--- | :--- | :--- |
| `WIDTH` | Entier (> 0) | Largeur de la grille du labyrinthe. |
| `HEIGHT` | Entier (> 0) | Hauteur de la grille du labyrinthe. |
| `ENTRY` | `x,y` | Coordonnées de la case de départ. |
| `EXIT` | `x,y` | Coordonnées de la case d'arrivée (différentes de `ENTRY`). |
| `OUTPUT_FILE` | `.txt` | Nom du fichier d'export où les données seront sauvegardées. |
| `PERFECT` | `true` ou `false` | `true` pour un labyrinthe parfait (chemin unique), `false` pour inclure des boucles. |
| `SEED` | Entier *(Optionnel)* | Graine aléatoire permettant de reproduire une génération spécifique. |

**Exemple de fichier `config.txt` valide :**
```text
# Configuration pour un grand labyrinthe imparfait
WIDTH=50
HEIGHT=50
ENTRY=0,0
EXIT=49,49
OUTPUT_FILE=solution_map.txt
PERFECT=false
SEED=42
```

### 📄 Format d'Export et Sortie de Données

Conformément aux exigences strictes du sujet, le projet génère ou traite un fichier de sortie structuré contenant l'intégralité des données topologiques du labyrinthe ainsi que sa solution. 

**Exemple de la structure de l'export généré :**

```text
91797B95539553BB95555157957BD3
A87AB8457C43BAA805153C51439456
C01400139178444047C7817C3C43D3
[...]
D6D547D47D47EC7C45557EEC57D6EE

0,0
29,29
ESSEEEEEESENESEEEESEEESEEESEESESESSSSSSSSEEESSSSSESSSEESSWSESS
```

**Analyse de la structure :**

* **1. La Grille (Hexadécimal) :** Chaque ligne correspond à une rangée du labyrinthe. L'optimisation réside dans l'encodage : chaque caractère hexadécimal (de `0` à `F`) représente une cellule unique. La valeur hexadécimale est un masque binaire (Bitmask) qui stocke l'état des 4 murs de la case (1 = Nord, 2 = Est, 4 = Sud, 8 = Ouest).
* **2. Point de Départ :** Les coordonnées de l'entrée du labyrinthe sous le format `X,Y`.
* **3. Point d'Arrivée :** Les coordonnées de la sortie ciblée sous le format `X,Y`.
* **4. Chemin de Résolution :** Une chaîne de caractères représentant les directions cardinales séquentielles (`N`=Nord, `S`=Sud, `E`=Est, `W`=Ouest). Cette séquence est le résultat direct de l'algorithme BFS, détaillant pas à pas la route optimale depuis le départ jusqu'à l'arrivée.

---

## 👥 Équipe et Gestion de Projet

Ce projet a été réalisé en binôme avec une division stricte des responsabilités afin de permettre un développement en parallèle fluide, en s'appuyant sur un format d'export de données pré-établi comme contrat d'interface.

* **Rôles et Répartition :**
    * **Dev A (`jfoeller`) :** En charge du rendu graphique, de l'interface utilisateur via MiniLibX, et de l'implémentation de l'algorithme de résolution (Pathfinding BFS) et de l'export de la solution. Realisation du package autonome. Gestion des arguments, du main.
    * **Dev B (`yafranco`) :** En charge de l'infrastructure logicielle, du moteur de génération (Prim), du parsing de la configuration, de l'export des données au format hexadécimal strict, de la redaction du Makefile et du README.md.
* **Déroulement et Planification :**
    * La phase initiale a consisté à définir conjointement et rigoureusement un tableau Google drive de repartition des taches dans la trame du projet.
    * Cette architecture découplée a permis de respecter le planning anticipé : le moteur (Dev B) pouvait générer des fichiers de tests en aveugle, pendant que l'interface (Dev A) pouvait être codée.
* **Rétrospective :**
    * *Ce qui a bien fonctionné :* La séparation nette des responsabilités a évité les conflits Git et a permis une grande autonomie. Le typage strict (`mypy`) a grandement facilité l'intégration finale des deux parties.
    * *Axes d'amélioration :* Communication autour des choix algorythmiques et techniques.

---

## 🤖 Ressources et Intelligence Artificielle

Dans le cadre de l'apprentissage et de la sécurisation du code, l'Intelligence Artificielle a été utilisée comme un outil d'assistance au développement tout au long du projet pour les tâches suivantes :

* **Analyse comparative :** Recherche des alternatives algorithmiques et production de benchmarks théoriques (notamment pour le choix entre Prim, Kruskal et le Recursive Backtracker).
* **Fiabilité et Tests :** Création d'instances de tests complexes, identification de *cas limites* (edge cases) et mise en évidence des exceptions potentielles.
* **Revue de code :** Vérification ponctuelle de la logique d'implémentation et de la complexité temporelle/spatiale des différentes fonctions. Aide au *merge* entre les deux branches du projet.
