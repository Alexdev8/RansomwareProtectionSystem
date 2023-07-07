import React from 'react';
import { Link } from 'react-router-dom';
import './NavBarClient.css';

export default function NavBarClient() {
  return (
    <div id="nav" className="sticky-nav">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/error">Erreur</Link>
        <Link to="/profile">Profile</Link>
        <a href="../../RPS-client.zip" download>Télécharger</a>
    </div>
  );
}
