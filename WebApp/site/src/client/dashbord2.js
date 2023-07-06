import React, { useState, useEffect } from 'react';
import NavBarClient from './components/NavBarClient';
import './dashboard.css';

export default function Dashboard({ user }) {
    const [machines, setMachines] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [machineName, setMachineName] = useState('');
    const [machineMac, setMachineMac] = useState('');

    useEffect(() => {
        // Charger les machines associées à clientId lors du montage du composant
        loadMachines();
    }, [user]);
    const loadMachines = () => {
        // Créer l'en-tête d'autorisation avec le token
        const headers = {
            Authorization: `Bearer ${user.connectionToken}`,
        };

        // Appel à l'API pour récupérer les machines associées à clientId
        fetch(`/api/client/${user.clientID}/machine`, { headers })
            .then(response => response.json())
            .then(data => {
                setMachines(data);
            })
            .catch(error => {
                console.error('Erreur lors du chargement des machines:', error);
            });
    };

    const handleAddMachine = () => {
        setShowForm(true);
    };

    const handleFormSubmit = e => {
        e.preventDefault();

        // Vérifier si les champs du formulaire sont remplis
        if (!machineName || !machineMac) {
            alert('Veuillez remplir tous les champs du formulaire.');
            return;
        }

        const newMachine = {
            name: machineName,
            machineAddress: machineMac
        };
        console.log(JSON.stringify(newMachine))
        // Créer l'en-tête d'autorisation avec le token
        const headers = {
            Authorization: `Bearer ${user.connectionToken}`,
            'Content-Type': 'application/json',
        };

        // Appel à l'API pour ajouter une nouvelle machine
        fetch(`/api/client/${user.clientID}/machine/register`, {
            method: 'POST',
            headers,
            body: JSON.stringify(newMachine),
        })
            .then(response => {
                if (response.ok) {
                    // Recharger la liste des machines après l'ajout réussi
                    loadMachines();
                    setMachineName('');
                    setMachineMac('');
                    setShowForm(false);
                } else {
                    alert('Erreur lors de l\'ajout de la machine.');
                }
            })
            .catch(error => {
                console.error('Erreur lors de l\'ajout de la machine:', error);
                alert('Erreur lors de l\'ajout de la machine.');
            });
    };

    const handleDeleteMachine = (machineId) => {
        // Demande de confirmation avant de supprimer une machine
        if (window.confirm('Êtes-vous sûr de vouloir supprimer cette machine ?')) {
            // Créer l'en-tête d'autorisation avec le token
            const headers = {
                Authorization: `Bearer ${user.connectionToken}`,
            };

            // Appel à l'API pour supprimer la machine
            fetch(`/api/client/${user.clientID}/machine/delete?machineId=${machineId}`, {
                method: 'DELETE',
                headers,
            })
                .then(response => {
                    if (response.ok) {
                        // Recharger la liste des machines après la suppression réussie
                        loadMachines();
                    } else {
                        alert('Erreur lors de la suppression de la machine.');
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de la suppression de la machine:', error);
                    alert('Erreur lors de la suppression de la machine.');
                });
        }
    };

    const handleUpdateMachine = (machineId) => {
        // Demander à l'utilisateur de fournir le nouveau nom et l'adresse MAC
        const newName = prompt('Entrez le nouveau nom de la machine :');
        const newMac = prompt('Entrez la nouvelle adresse MAC de la machine :');

        // Vérifier si les champs sont remplis
        if (!newName || !newMac) {
            alert('Veuillez remplir tous les champs.');
            return;
        }

        const updatedMachine = {
            name: newName,
            machineAddress: newMac,
        };

        // Créer l'en-tête d'autorisation avec le token
        const headers = {
            Authorization: `Bearer ${user.connectionToken}`,
            'Content-Type': 'application/json',
        };

        // Appel à l'API pour mettre à jour la machine
        fetch(`/api/client/${user.clientID}/machine/update?machineId=${machineId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify(updatedMachine),
        })
            .then(response => {
                if (response.ok) {
                    // Recharger la liste des machines après la mise à jour réussie
                    loadMachines();
                } else {
                    alert('Erreur lors de la mise à jour de la machine.');
                }
            })
            .catch(error => {
                console.error('Erreur lors de la mise à jour de la machine:', error);
                alert('Erreur lors de la mise à jour de la machine.');
            });
    };

    return (
        <div>
            <NavBarClient />
            <button onClick={handleAddMachine}>Ajouter une machine</button>
            {showForm && (
                <form onSubmit={handleFormSubmit}>
                    <label>Nom :</label>
                    <input type="text" value={machineName} onChange={(e) => setMachineName(e.target.value)} />
                    <label>Adresse MAC :</label>
                    <input type="text" value={machineMac} onChange={(e) => setMachineMac(e.target.value)} />
                    <button type="submit">Ajouter</button>
                </form>
            )}
            <table>
                <thead>
                <tr>
                    <th>Adresse MAC</th>
                    <th>Nom</th>
                    <th>État</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                {machines.map((machine) => (
                    <tr key={machine.machineID}>
                        <td>{machine.machineAddress}</td>
                        <td>{machine.name}</td>
                        <td>{machine.state === 1 ? 'Sain' : 'Non sain'}</td>
                        <td>
                            <button onClick={() => handleUpdateMachine(machine.machineID)}>Modifier</button>
                            <button onClick={() => handleDeleteMachine(machine.machineID)}>Supprimer</button>
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}
