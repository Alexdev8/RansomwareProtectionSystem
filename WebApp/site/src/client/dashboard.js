import React, { useState, useEffect } from 'react';
import NavBarClient from './components/NavBarClient';
import './dashboard.css';

export default function Dashboard({ user }) {
    const [machines, setMachines] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [machineName, setMachineName] = useState('');
    const [machineMac, setMachineMac] = useState('');
    const [editingMachineId, setEditingMachineId] = useState(null);
    const [editMachineName, setEditMachineName] = useState('');
    const [editMachineMac, setEditMachineMac] = useState('');

    useEffect(() => {
        // Charger les machines associées à clientId lors du montage du composant
        loadMachines();
    }, [user]);

    const compareByState = (a, b) => {
        if (a.state === 0 && b.state === 1) {
            return -1; // Place les machines en état non sain avant celles en état sain
        } else if (a.state === 1 && b.state === 0) {
            return 1; // Place les machines en état sain après celles en état non sain
        } else {
            return 0; // Conserve l'ordre d'origine des machines ayant le même état
        }
    };

    const loadMachines = () => {
        // Créer l'en-tête d'autorisation avec le token
        const headers = {
            Authorization: `Bearer ${user.connectionToken}`,
        };

        // Appel à l'API pour récupérer les machines associées à clientId
        fetch(`/api/client/${user.clientID}/machine`, { headers })
            .then(response => response.json())
            .then(data => {
                // Trier les machines par état non sain en premier
                const sortedMachines = data.sort(compareByState);
                setMachines(sortedMachines);
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
            machineAddress: machineMac,
        };

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

    const handleDeleteMachine = machineId => {
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

    const handleUpdateMachine = machineId => {
        // Vérifier si les champs sont remplis
        if (!editMachineName || !editMachineMac) {
            alert('Veuillez remplir tous les champs.');
            return;
        }

        const updatedMachine = {
            name: editMachineName,
            machineAddress: editMachineMac,
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
                    setEditingMachineId(null);
                } else {
                    alert('Erreur lors de la mise à jour de la machine.');
                }
            })
            .catch(error => {
                console.error('Erreur lors de la mise à jour de la machine:', error);
                alert('Erreur lors de la mise à jour de la machine.');
            });
    };

    const handleEditMachine = (machineId, currentName, currentMac) => {
        setEditingMachineId(machineId);
        setEditMachineName(currentName);
        setEditMachineMac(currentMac);
    };

    const handleToggleMachineState = (machineId, currentState) => {
        const newState = currentState === 0 ? 1 : 0;

        // Créer l'en-tête d'autorisation avec le token
        const headers = {
            Authorization: `Bearer ${user.connectionToken}`,
            'Content-Type': 'application/json',
        };

        // Appel à l'API pour changer l'état de la machine
        fetch(`/api/client/${user.clientID}/machine/state?machineId=${machineId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ state: newState }),
        })
            .then(response => {
                if (response.ok) {
                    loadMachines();
                } else {
                    alert('Erreur lors du changement d\'état de la machine.');
                }
            })
            .catch(error => {
                console.error('Erreur lors du changement d\'état de la machine:', error);
                alert('Erreur lors du changement d\'état de la machine.');
            });
    };

    return (
        <div>
            <NavBarClient />
            <button onClick={handleAddMachine}>Ajouter une machine</button>
            {showForm && (
                <form onSubmit={handleFormSubmit}>
                    <label>Nom :</label>
                    <input type="text" value={machineName} onChange={e => setMachineName(e.target.value)} />
                    <label>Adresse MAC :</label>
                    <input type="text" value={machineMac} onChange={e => setMachineMac(e.target.value)} />
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
                {machines.map(machine => (
                    <tr key={machine.machineID}>
                        <td>
                            {machine.machineID === editingMachineId ? (
                                <input
                                    type="text"
                                    value={editMachineMac}
                                    onChange={e => setEditMachineMac(e.target.value)}
                                />
                            ) : (
                                machine.machineAddress
                            )}
                        </td>
                        <td>
                            {machine.machineID === editingMachineId ? (
                                <input
                                    type="text"
                                    value={editMachineName}
                                    onChange={e => setEditMachineName(e.target.value)}
                                />
                            ) : (
                                machine.name
                            )}
                        </td>
                        <td>
                            {machine.machineID === editingMachineId ? (
                                <>
                                    <input
                                        type="text"
                                        value={editMachineMac}
                                        onChange={e => setEditMachineMac(e.target.value)}
                                    />
                                    <input
                                        type="text"
                                        value={editMachineName}
                                        onChange={e => setEditMachineName(e.target.value)}
                                    />
                                </>
                            ) : (
                                <>
                                    {machine.state === 1 ? 'Sain' : 'Non sain'}
                                </>
                            )}
                        </td>
                        <td>
                            {machine.machineID === editingMachineId ? (
                                <>
                                    <button onClick={() => handleUpdateMachine(machine.machineID)}>Enregistrer</button>
                                    <button onClick={() => setEditingMachineId(null)}>Annuler</button>
                                </>
                            ) : (
                                <button onClick={() => handleEditMachine(machine.machineID, machine.name, machine.machineAddress)}>
                                    Modifier
                                </button>
                            )}
                            <button onClick={() => handleDeleteMachine(machine.machineID)}>Supprimer</button>
                            <button onClick={() => handleToggleMachineState(machine.machineID, machine.state)}>
                                Changer l'état
                            </button>
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}
