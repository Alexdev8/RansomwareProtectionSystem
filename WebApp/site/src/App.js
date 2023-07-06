import React, {useState} from 'react';
import {BrowserRouter, BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import HomePage from './guest/views/HomePage';
import SecurityPolicy from './guest/views/SecurityPolicy';
import Contact from './guest/views/Contact';
import './App.css';
import Dashboard from './client/dashboard';
import {LogIn, SignIn} from './SingIn.js';


function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  let expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) === 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

export default function App() {
  const [user, setUser] = useState((!!getCookie("user")) ? {email: getCookie("user")} : null);
  const [prevLocation, setPrevLocation] = useState("/");
  return (
    <BrowserRouter>
      <div id="app">
        <header user={user} setUser={setUser}>
          <div className="header-style">
            <div className="logo-container">
              <img
                className="logo"
                src="./RPS.png"
                alt="Logo de HackFactorizz"
              />
            </div>
            <div className="text-container">
              <h1 className="title">HackFactorizz</h1>
              <h3 className="slogan">Protection optimale contre les ransomwares</h3>
            </div>
          </div>
        </header>

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/security-policy" element={<SecurityPolicy />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/dashboard" element={<Dashboard user={user}/>} />
          <Route path="/SingIn" element={<SignIn />} />
          <Route path="/LogIn" element={<LogIn originPath={prevLocation} user={user} setUser={setUser} setCookie={setCookie}/>} />
        </Routes>

        <footer>
          <div className="footerbar">
            <ul>
              <li>&copy; 2023 Application Anti-Ransomware. Tous droits réservés.</li>
              <br />
              <li>
                <a href="/security-policy">Politique de sécurité</a>
              </li>
              <br />
              <li>
                <a href="/contact">Contactez-nous</a>
              </li>
            </ul>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}
