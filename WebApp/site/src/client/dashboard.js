import React, { useState } from 'react';
import NavBarClient from './components/NavBarClient';
import './dashboard.css';

export default function Dashboard(prop) {
    const [computers, setComputers] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [computerName, setComputerName] = useState('');
    const [computerSerie, setComputerSerie] = useState('');
    console.log(prop.user);
    console.log(prop.user.clientID);
    console.log(prop.user.connectionToken);
    const handleAddComputer = () => {
        setShowForm(true);
    };

    const handleFormSubmit = (e) => {
        e.preventDefault();
        const newComputer = {
            nserie: computerSerie,
            name: computerName,
            state: 'Sain',
        };
        setComputers([...computers, newComputer]);
        setComputerName('');
        setComputerSerie('');
        setShowForm(false);
    };

    const handleDeleteComputer = (index) => {
        setComputers(computers.filter((_, i) => i !== index));
    };

    const handleToggleState = (index) => {
        setComputers(prevComputers => {
            const updatedComputers = [...prevComputers];
            const computer = { ...updatedComputers[index] };
            computer.state = computer.state === 'Sain' ? 'Non sain' : 'Sain';
            updatedComputers[index] = computer;
            return updatedComputers;
        });
    };

    return (
        <div>
            <NavBarClient />
            <button onClick={handleAddComputer}>Ajouter un ordinateur</button>
            {showForm && (
                <form onSubmit={handleFormSubmit}>
                    <label>N° série:</label>
                    <input type="text" value={computerSerie} onChange={(e) => setComputerSerie(e.target.value)} />
                    <label>Nom :</label>
                    <input type="text" value={computerName} onChange={(e) => setComputerName(e.target.value)} />
                    <button type="submit">Ajouter</button>
                </form>
            )}
            <table>
                <thead>
                <tr>
                    <th>N° série</th>
                    <th>Nom</th>
                    <th>État</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                {computers.map((computer, index) => (
                    <tr key={index}>
                        <td>{computer.nserie}</td>
                        <td>{computer.name}</td>
                        <td>{computer.state}</td>
                        <td>
                            <button onClick={() => handleToggleState(index)}>Changer l'état</button>
                            <button onClick={() => handleDeleteComputer(index)}>Supprimer</button>
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}