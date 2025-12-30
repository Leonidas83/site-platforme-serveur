

import pandas as pd

# Initialisation d'un DataFrame vide pour les services
# Dans une application réelle, ces données viendraient d'une base de données
services_df = pd.DataFrame(columns=['id', 'name', 'description', 'price', 'features'])

def get_next_service_id():
    """Génère un ID unique pour un nouveau service."""
    global services_df
    if services_df.empty:
        return 1
    return services_df['id'].max() + 1

# --- Fonctions de gestion des services ---

def add_service(name, description, price, features):
    """Ajoute un nouveau service au DataFrame."""
    global services_df
    service_id = get_next_service_id()
    new_service = pd.DataFrame([{'id': service_id, 'name': name, 'description': description, 'price': price, 'features': features}])
    services_df = pd.concat([services_df, new_service], ignore_index=True)
    print(f"Service '{name}' (ID: {service_id}) ajouté.")
    return service_id

def get_all_services():
    """Retourne tous les services disponibles."""
    global services_df
    return services_df

def get_service_by_id(service_id):
    """Retourne un service par son ID."""
    global services_df
    service_found = services_df[services_df['id'] == service_id]
    return service_found.to_dict(orient='records')[0] if not service_found.empty else None

def update_service(service_id, name=None, description=None, price=None, features=None):
    """Met à jour les informations d'un service existant."""
    global services_df
    idx = services_df[services_df['id'] == service_id].index
    if not idx.empty:
        if name: services_df.loc[idx, 'name'] = name
        if description: services_df.loc[idx, 'description'] = description
        if price is not None: services_df.loc[idx, 'price'] = price
        if features: services_df.loc[idx, 'features'] = features
        print(f"Service ID {service_id} mis à jour.")
        return True
    print(f"Service ID {service_id} non trouvé.")
    return False

def delete_service(service_id):
    """Supprime un service par son ID."""
    global services_df
    initial_rows = len(services_df)
    services_df = services_df[services_df['id'] != service_id].reset_index(drop=True)
    if len(services_df) < initial_rows:
        print(f"Service ID {service_id} supprimé.")
        return True
    print(f"Service ID {service_id} non trouvé.")
    return False


# Exemple d'utilisation (vous pouvez mettre cela dans un script séparé ou après la définition des fonctions)
if __name__ == '__main__':
    print("--- Exécution des exemples de gestion des services ---")
    add_service("Hébergement Basique", "Espace disque 10GB, Trafic 100GB", 9.99, ["10GB SSD", "100GB Trafic", "1 Domaine"])
    add_service("Hébergement Premium", "Espace disque 50GB, Trafic Illimité, SSL", 24.99, ["50GB SSD", "Trafic Illimité", "5 Domaines", "Certificat SSL"])
    add_service("Serveur Dédié", "Serveur puissant pour gros projets", 99.99, ["CPU 4 cœurs", "RAM 16GB", "Disque 1TB SSD", "IP dédiée"])

    print("\n--- Tous les services ---")
    print(get_all_services())

    print("\n--- Service ID 2 ---")
    print(get_service_by_id(2))

    update_service(1, description="Espace disque 20GB, Trafic 200GB", price=12.99)
    delete_service(3)

    print("\n--- Services après modifications ---")
    print(get_all_services())
