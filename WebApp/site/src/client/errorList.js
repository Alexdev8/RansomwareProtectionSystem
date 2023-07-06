import React, { useEffect, useState } from 'react';

function ErrorList({user}) {
    const [errors, setErrors] = useState([]);

    useEffect(() => {
        fetch(`/api/client/${user.clientID}/machine/error`)
            .then(response => response.json())
            .then(data => setErrors(data))
            .catch(error => console.error('Error:', error));
    }, []);

    return (
        <div>
            <h1>Error List</h1>
            <table>
                <thead>
                <tr>
                    <th>Date</th>
                    <th>Nom de la machine</th>
                    <th>Description de l'erreur</th>
                </tr>
                </thead>
                <tbody>
                {errors.map(error => (
                    <tr key={error.errorID}>
                        <td>{error.date}</td>
                        <td>{error.name}</td>
                        <td>{error.description}</td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}

export default ErrorList;
