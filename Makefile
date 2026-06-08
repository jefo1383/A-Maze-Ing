# ==============================================================================
# Variables
# ==============================================================================
VENV = venv
PYTHON = ./$(VENV)/bin/python3
MAIN = a_maze_ing.py
CONFIG = config.txt
FLAKE8_EXCLUDE = --exclude=venv,mlx_CLXV,dist,*.egg-info,__pycache__,.mypy_cache,.git
MYPY_EXCLUDE = --exclude 'venv|mlx_CLXV|dist|\.egg-info'

# ==============================================================================
# Règles obligatoires
# ==============================================================================
.PHONY: install run debug clean fclean re lint lint-strict

# Installe les dépendances du projet
install:
	@echo "🛠️ Création de l'environnement virtuel..."
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
		$(PYTHON) -m pip install --upgrade pip; \
	fi
	@echo "📦 Renommage et installation de la MiniLibX..."
	@if [ -f mlx-2.2-py3-ubuntu-any.whl ]; then \
		mv mlx-2.2-py3-ubuntu-any.whl mlx-2.2-py3-none-any.whl; \
	fi
	@if [ -f mlx-2.2-py3-none-any.whl ]; then \
		$(PYTHON) -m pip install mlx-2.2-py3-none-any.whl; \
		echo "✅ Installation terminée dans ./$(VENV)"; \
	else \
		echo "❌ ERREUR : Fichier MiniLibX introuvable !"; \
		echo "Veuillez télécharger les ressources du projet depuis l'intranet 42."; \
		echo "Placez le fichier 'mlx-2.2-py3-ubuntu-any.whl' à la racine de ce dépôt,"; \
		echo "puis relancez la commande 'make install'.\n"; \
		exit 1; \
	fi
	@echo "🧩 Installation du package mazegen local..."
	@if ls mazegen-*.whl 1> /dev/null 2>&1; then \
		$(PYTHON) -m pip install mazegen-*.whl; \
		echo "✅ Installation terminée dans ./$(VENV)"; \
	else \
		echo "❌ ERREUR : Package mazegen-*.whl introuvable à la racine."; \
		exit 1; \
	fi

# Exécute le script principal avec le fichier de configuration par défaut
run:
	@if [ ! -d "$(VENV)" ]; then echo "❌ Erreur: Faites 'make install' d'abord."; exit 1; fi
	$(PYTHON) $(MAIN) $(CONFIG)

# Lance le script avec le débogueur intégré de Python (pdb)
debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

# Supprime les fichiers temporaires et les caches
clean:
	rm -rf __pycache__ .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Nettoyage complet : clean + suppression de l'environnement virtuel et des builds
fclean: clean
	rm -rf venv dist *.egg-info

# Recompile / Réinstalle tout depuis zéro
re: fclean install

# Analyse statique du code (Linting) avec les flags requis par le PDF
lint:
	flake8 $(FLAKE8_EXCLUDE) .
	mypy . $(MYPY_EXCLUDE) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# Analyse statique stricte (Optionnelle mais recommandée par 42)
lint-strict:
	flake8 $(FLAKE8_EXCLUDE) .
	mypy . $(MYPY_EXCLUDE) --strict --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs