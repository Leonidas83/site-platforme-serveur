
# Mon Projet d'Hébergement de Services

Ce dépôt contient le code backend (API Flask avec SQLite) et une interface frontend simple pour la gestion de services d'hébergement, d'utilisateurs et de leurs abonnements.

## Structure du Projet

```
mon-projet-hebergement/
├── app.py                      # Application Flask principale avec les routes API
├── initialize_database.py      # Script pour créer et initialiser la base de données SQLite
├── extended_database.db        # Fichier de la base de données SQLite (généré par initialize_database.py)
├── requirements.txt            # Dépendances Python
├── index.html                  # Interface utilisateur frontend HTML
├── script.js                   # JavaScript pour l'interaction frontend avec l'API
├── .gitignore                  # Fichiers à ignorer par Git
├── LICENSE                     # Informations sur la licence du projet
└── README.md                   # Ce fichier
```

## Installation

1.  **Cloner le dépôt** :
    ```bash
    git clone https://github.com/votre-utilisateur/mon-projet-hebergement.git
    cd mon-projet-hebergement
    ```
2.  **Créer un environnement virtuel (recommandé)** :
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate
    ```
3.  **Installer les dépendances Python** :
    ```bash
    pip install -r requirements.txt
    ```

## Utilisation

1.  **Initialiser la base de données** :
    Exécutez ce script une seule fois pour créer la base de données `extended_database.db` et la peupler avec des données initiales.
    ```bash
    python initialize_database.py
    ```

2.  **Lancer le serveur Flask** :
    ```bash
    export FLASK_APP=app.py
    export FLASK_ENV=development # Pour le mode développement (débogage)
    flask run
    ```
    Le serveur sera accessible sur `http://127.0.0.1:5000/`.

3.  **Ouvrir l'interface Frontend** :
    Ouvrez simplement le fichier `index.html` dans votre navigateur web.
    *Note : Le `script.js` de l'interface est configuré pour communiquer avec l'API sur `http://127.0.0.1:5000`.*

## Routes API Disponibles (via `app.py`)

*   **Utilisateurs** :
    *   `POST /users`: Créer un nouvel utilisateur.
    *   `GET /users`: Récupérer tous les utilisateurs.
    *   `GET /users/<int:user_id>`: Récupérer un utilisateur par ID.
    *   `PUT /users/<int:user_id>`: Mettre à jour un utilisateur.
    *   `DELETE /users/<int:user_id>`: Supprimer un utilisateur.
    *   `POST /login`: Authentification utilisateur.
    *   `GET /search/users?email=...&first_name=...&last_name=...`: Rechercher des utilisateurs.
*   **Services** :
    *   `GET /services`: Récupérer tous les services.
    *   `GET /services/<int:service_id>`: Récupérer un service par ID.
*   **Abonnements (User-Services)** :
    *   `GET /users/<int:user_id>/subscriptions`: Récupérer les abonnements d'un utilisateur.
    *   `GET /users/<int:user_id>/subscriptions/<int:service_id>`: Récupérer un abonnement spécifique.
    *   `POST /users/<int:user_id>/subscriptions`: Ajouter un abonnement.
    *   `PUT /users/<int:user_id>/subscriptions/<int:service_id>`: Mettre à jour un abonnement.
    *   `DELETE /users/<int:user_id>/subscriptions/<int:service_id>`: Supprimer un abonnement.

## Développement Futur

Des pistes d'amélioration incluent l'implémentation d'une authentification et autorisation robustes (par exemple, JWT), une interface utilisateur plus dynamique et l'ajout de fonctionnalités de gestion administrative.
