import React from 'react';
import './NavBar.css';
import {Link} from "react-router-dom";

export default function NavBar() {
  return (
    <div id="nav" className="sticky-nav">
        <a href="#about-us">Qui sommes-nous ?</a>
        <a href="#context">Le contexte</a>
        <a href="#objective">L'objectif</a>
        <a href="#rps-solution">RPS Solution</a>
        <a href="#features">Fonctionnalités</a>
        <a href="#pricing">Tarification</a>
        <a href="#advantages">Bénéfices</a>
        <a href="#automation">Automatisation</a>
        <a href="#download">Télécharger</a>
        <Link to="/SignIn">S'inscrire</Link>
        <Link to="/LogIn">Se connecter</Link>
    </div>
  );
}
