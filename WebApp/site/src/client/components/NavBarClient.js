import React from 'react';
import '../App.css';

export default function NavBar() {
  return (
    <div id="nav" className="sticky-nav">
      <a href="#dashboard">Dashboard</a>
      <a href="#error">Erreur</a>
      <a href="#back-up">Sauvegarde</a>
      <a href="#profil">Profile</a>
    </div>
  );
}
