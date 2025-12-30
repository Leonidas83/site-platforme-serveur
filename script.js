
const API_BASE_URL = 'http://127.0.0.1:5000'; // Remplacez par l'URL de votre API Flask si elle est différente (ex: en production)

// Fonction d'aide pour afficher les réponses de l'API
function displayResponse(elementId, data, isError = false) {
    const responseBox = document.getElementById(elementId);
    responseBox.style.color = isError ? 'red' : 'black';
    responseBox.textContent = JSON.stringify(data, null, 2);
}

let loggedInUserId = null; // Variable pour stocker l'ID de l'utilisateur connecté

// --- Fonctions de Gestion des Utilisateurs ---

async function registerUser() {
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const firstName = document.getElementById('regFirstName').value;
    const lastName = document.getElementById('regLastName').value;

    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, first_name: firstName, last_name: lastName }),
        });
        const data = await response.json();
        if (response.ok) {
            displayResponse('regResponse', data);
        } else {
            displayResponse('regResponse', data, true);
        }
    } catch (error) {
        displayResponse('regResponse', { message: 'Erreur réseau ou API non disponible', error: error.message }, true);
    }
}

async function loginUser() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        const data = await response.json();
        if (response.ok) {
            loggedInUserId = data.user_id;
            document.getElementById('loggedInUserId').textContent = loggedInUserId;
            displayResponse('loginResponse', data);
            // Vous pouvez stocker loggedInUserId dans sessionStorage ou localStorage ici pour persister la connexion
        } else {
            loggedInUserId = null;
            document.getElementById('loggedInUserId').textContent = 'None';
            displayResponse('loginResponse', data, true);
        }
    } catch (error) {
        displayResponse('loginResponse', { message: 'Erreur réseau ou API non disponible', error: error.message }, true);
    }
}

async function searchUsers() {
    const email = document.getElementById('searchEmail').value;
    const firstName = document.getElementById('searchFirstName').value;
    const lastName = document.getElementById('searchLastName').value;

    const params = new URLSearchParams();
    if (email) params.append('email', email);
    if (firstName) params.append('first_name', firstName);
    if (lastName) params.append('last_name', lastName);

    try {
        const response = await fetch(`${API_BASE_URL}/search/users?${params.toString()}`);
        const data = await response.json();
        if (response.ok) {
            displayResponse('searchUsersResponse', data);
        } else {
            displayResponse('searchUsersResponse', data, true);
        }
    } catch (error) {
        displayResponse('searchUsersResponse', { message: 'Erreur réseau ou API non disponible', error: error.message }, true);
    }
}

// --- Fonctions de Gestion des Services ---

async function getAllServices() {
    try {
        const response = await fetch(`${API_BASE_URL}/services`);
        const data = await response.json();
        if (response.ok) {
            displayResponse('servicesResponse', data);
        } else {
            displayResponse('servicesResponse', data, true);
        }
    } catch (error) {
        displayResponse('servicesResponse', { message: 'Erreur réseau ou API non disponible', error: error.message }, true);
    }
}

// --- Fonctions de Gestion des Abonnements ---

async function getUserSubscriptions() {
    const userId = document.getElementById('subUserId').value;
    if (!userId) {
        displayResponse('subsResponse', { message: 'Veuillez entrer un ID utilisateur' }, true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/subscriptions`);
        const data = await response.json();
        if (response.ok) {
            displayResponse('subsResponse', data);
        } else {
            displayResponse('subsResponse', data, true);
        }
    } catch (error) {
        displayResponse('subsResponse', { message: 'Erreur réseau ou API non disponible', error: error.message }, true);
    }
}

async function addSubscription() {
    const userId = document.getElementById('subUserId').value;
    const serviceId = document.getElementById('subServiceId').value;
    const startDate = document.getElementById('subStartDate').value;
    const endDate = document.getElementById('subEndDate').value;
    const active = document.getElementById('subActive').value;

    if (!userId || !serviceId || !startDate) {
        displayResponse('subsResponse', { message: 'L\'ID Utilisateur, l\'ID Service et la Date de Début sont requis' }, true);
        return;
    }

    const body = {
        service_id: parseInt(serviceId),
        start_date: startDate,
        active: parseInt(active)
    };
    if (endDate) {
        body.end_date = endDate;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/subscriptions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });
        const data = await response.json();
        if (response.ok) {
            displayResponse('subsResponse', data);
            getUserSubscriptions(); // Rafraîchir la liste des abonnements
        } else {
            displayResponse('subsResponse', data, true);
        }
    } catch (error) {
        displayResponse('subsResponse', { message: 'Erreur réseau ou API non disponible', error: error.message }, true);
    }
}

async function updateSubscription() {
    const userId = document.getElementById('subUserId').value;
    const serviceId = document.getElementById('subServiceId').value;
    const endDate = document.getElementById('subEndDate').value;
    const active = document.getElementById('subActive').value;

    if (!userId || !serviceId) {
        displayResponse('subsResponse', { message: 'L\'ID Utilisateur et l\'ID Service sont requis pour la mise à jour' }, true);
        return;
    }

    const body = {};
    if (endDate) {
        body.end_date = endDate;
    }
    if (active !== null && active !== '') {
        body.active = parseInt(active);
    }

    if (Object.keys(body).length === 0) {
        displayResponse('subsResponse', { message: 'Aucune donnée de mise à jour fournie (end_date ou active)' }, true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/subscriptions/${serviceId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });
        const data = await response.json();
        if (response.ok) {
            displayResponse('subsResponse', data);
            getUserSubscriptions(); // Rafraîchir la liste des abonnements
        } else {
            displayResponse('subsResponse', data, true);
        }
    } catch (error) {
        displayResponse('subsResponse', { message: 'Erreur réseau ou API non disponible', error: error.message }, true);
    }
}

async function deleteSubscription() {
    const userId = document.getElementById('subUserId').value;
    const serviceId = document.getElementById('subServiceId').value;

    if (!userId || !serviceId) {
        displayResponse('subsResponse', { message: 'L\'ID Utilisateur et l\'ID Service sont requis pour la suppression' }, true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/subscriptions/${serviceId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json();
        if (response.ok) {
            displayResponse('subsResponse', data);
            getUserSubscriptions(); // Rafraîchir la liste des abonnements
        } else {
            displayResponse('subsResponse', data, true);
        }
    } catch (error) {
        displayResponse('subsResponse', { message: 'Erreur réseau ou API non disponible', error: error.message }, true);
    }
}

// Initialiser loggedInUserId si déjà défini (par exemple, depuis sessionStorage si implémenté entièrement)
window.onload = () => {
    const storedUserId = sessionStorage.getItem('loggedInUserId'); // Exemple de persistance de connexion
    if (storedUserId) {
        loggedInUserId = parseInt(storedUserId);
        document.getElementById('loggedInUserId').textContent = loggedInUserId;
    }
};
