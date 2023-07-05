import React, {useEffect, useRef, useState} from "react";
import {Link, useLocation, useNavigate} from "react-router-dom";
function SignIn(){
    return(
        <div>
            <h1>Sign in</h1>
            <div className="userData">
                <div className="accountEmail">
                    <span className="material-symbols-outlined"> person </span>
                    <input type="email" id="username" placeholder="Username or Email"/>
                </div>
                <div className="accountPassword">
                    <span className="material-symbols-outlined"> lock </span>
                    <input type="password" id="password" placeholder="Password"/>
                </div>
            </div>
            <button>Connexion</button>
            <div className="linkaccount">
                <a>Forgot Password?</a>
                <a>Create an account</a>
            </div>

        </div>
    )
}

function AccountBtn({user, setUser, setCookie}) {
    const [hidden, setHidden] = useState(true);
    const popup = useRef(null);
    const navigate = useNavigate();
    const location = useLocation();

    function handleClickOutside(event) {
        if (popup.current && !popup.current.contains(event.target)) {
            setHidden(true);
        }
    }

    useEffect(() => {
        // Bind the event listener
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            // Unbind the event listener on clean up
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <div className="account-btn" ref={popup}>
            <span className="icon-btn material-symbols-outlined" onClick={() => (hidden) ? setHidden(false) : setHidden(true)} tabIndex="0">
            person
            </span>
            <div className={(hidden) ? "hidden" : ""} id="account-btn-popup">
                {
                    (user === null) ?
                        <div>
                            <button className="popup-button" onClick={() => {
                                navigate("./account/login");
                                setHidden(true);
                            }}>Log in</button>
                            <button className="popup-button" onClick={() => {
                                navigate("./account/signin");
                                setHidden(true);
                            }}>Create an account</button>
                        </div>
                        :
                        <div>
                            <button className="popup-button" onClick={() => {
                                navigate("./account");
                                setHidden(true);
                            }}>Profile</button>
                            <button className="logout-btn popup-button" onClick={() => {
                                setUser(null);
                                setCookie("user", "", -1);
                                setHidden(true);
                                console.log(location.pathname);
                                if (location.pathname === "/account" || location.pathname === "/account/") {
                                    navigate("/");
                                }
                            }}>Log out</button>
                        </div>
                }
            </div>
        </div>
    )
}