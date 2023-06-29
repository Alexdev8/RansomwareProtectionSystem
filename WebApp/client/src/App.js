import React, { useState } from 'react';
import './App.css';

function App() {
  const [computers, setComputers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [computerName, setComputerName] = useState('');
  const [countNonSain, setCountNonSain] = useState(0);

  const handleAddComputer = () => {
    setShowForm(true);
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();

    // Créer un nouvel objet pour représenter les caractéristiques de l'ordinateur
    const newComputer = {
      name: computerName,
      state: 'sain',
    };

    // Ajouter le nouvel ordinateur à la liste des ordinateurs
    setComputers([...computers, newComputer]);

    // Réinitialiser les valeurs du formulaire
    setComputerName('');

    // Masquer le formulaire
    setShowForm(false);
  };

  const handleToggleState = (index) => {
    setComputers(prevComputers => {
      const updatedComputers = [...prevComputers];
      const computer = {...updatedComputers[index]};
      if (computer.state === 'sain') {
        computer.state = 'non sain';
      } else {
        computer.state = 'sain';
      }
      updatedComputers[index] = computer;

      const nonSainCount = updatedComputers.filter(computer => computer.state === 'non sain').length;
      setCountNonSain(nonSainCount);

      return updatedComputers;
    });
  };

  return (
      <div>
        <h2>Nombre d'ordinateurs non sains : {countNonSain}</h2>
        <button onClick={handleAddComputer}>Ajouter un ordinateur</button>
        {showForm && (
            <form onSubmit={handleFormSubmit}>
              <label>Nom :</label>
              <input
                  type="text"
                  value={computerName}
                  onChange={(e) => setComputerName(e.target.value)}
              />

              <button type="submit">Ajouter</button>
            </form>
        )}

        <table>
          <thead>
          <tr>
            <th>Nom</th>
            <th>État</th>
            <th></th>
          </tr>
          </thead>
          <tbody>
          {computers
              .sort((a, b) => (a.state === 'non sain' ? -1 : 1))
              .map((computer, index) => (
                  <tr
                      key={index}
                      className={computer.state === 'non sain' ? 'red-row' : ''}
                  >
                    <td>{computer.name}</td>
                    <td>
                      {computer.state}
                    </td>
                    <td>
                      <button onClick={() => handleToggleState(index)}>
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

export default App;