import {Link, useNavigate} from "react-router-dom";
import {useEffect, useRef, useState} from "react";
import axios from "axios";

const emailData = [
    {
        id: "email",
        title: "Addresse mail",
        type: "email",
        example: "baker.justin@gmail.com"
    },
    {
        id: "email2",
        type: "email",
        title: "Confirmation de l'addresse mail",
        example: "baker.justin@gmail.com"
    }
]


const nameData = [
    {
        id: "firstName",
        type: "text",
        title: "First Name",
        example: "Justin"
    },
    {
        id: "lastName",
        type: "text",
        title: "Last Name",
        example: "Baker"
    }
]

const password = [
    {
        id: "new-password",
        type: "password",
        title: "Mot de passe",
    },
    {
        id: "password2",
        type: "password",
        title: "Confirmation du mot de passe",
    }
]

function normalizeInput(input) {
    return input.trim()
}

function matchRegex(regex, string) {
    return regex.test(string);
}

function AccountInformation({months, name, email}){
    const navigate = useNavigate();

    const form = useRef(null);
    const [formInputsValidity, setFormInputsValidity] = useState({"firstName": true, "lastName": true, "date": true, "email": true, "email2": true, "phone-number": true, "new-password": true, "password2": true});
    function getBirthDate() {
        return form.current["birthdate-year"].value + '-' + form.current["birthdate-month"].value + '-' + form.current["birthdate-day"].value;
    }

    function sendForm(e) {
        e.preventDefault();
        if (checkData()) {
            axios({
                method: 'post',
                url: '/api/client/register',
                timeout: 4000, // 4 seconds timeout
                data: {
                    firstName: normalizeInput(form.current["firstName"].value),
                    lastName: normalizeInput(form.current["lastName"].value),
                    email: normalizeInput(form.current["email"].value),
                    password: form.current["new-password"].value,
                    phone: (normalizeInput(form.current["phone-number"].value) !== "") ? normalizeInput(form.current["phone-number"].value): null,
                    company: form.current["company-name"].value,
                    subscription: form.current["subscription"].value
                }
            })
                .then(response => {
                    if (response.status === 201 && response.statusText === "Created") {
                        navigate("../dashboard", {replace: true});
                    }
                })
                .catch(error => {
                    if (error.response.data === "ER_DUP_ENTRY") {
                        alert("An account already exist with this email");
                    }
                    else {
                        console.error('error: ', error);
                    }
                });
        }
    }

    function checkData() {
        let formValid = true;
        const email = document.getElementById("email").value;
        const emailConfirmation = document.getElementById("email2").value;

        const password = document.getElementById("new-password").value;
        const passwordConfirmation = document.getElementById("password2").value;

        //Check for empty inputs
        if (normalizeInput(form.current["firstName"].value) === "") {
            console.log("error: Empty inputs");
            setFormInputsValidity({...formInputsValidity, "firstName": false});
            formValid = false;
        }
        if (normalizeInput(form.current["lastName"].value) === "") {
            console.log("error: Empty inputs");
            setFormInputsValidity({...formInputsValidity, "lastName": false});
            formValid = false;
        }
        if (normalizeInput(form.current["email"].value) === "") {
            console.log("error: Empty inputs");
            setFormInputsValidity({...formInputsValidity, "email": false});
            formValid = false;
        }
        if (normalizeInput(form.current["new-password"].value) === "") {
            console.log("error: Empty inputs");
            setFormInputsValidity({...formInputsValidity, "new-password": false});
            formValid = false;
        }

        //Check for email validation
        if (!matchRegex(/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, normalizeInput(form.current["email"].value))) {
            console.log("error: invalid email");
            setFormInputsValidity({...formInputsValidity, "email": false});
            formValid = false;
        }

        //Check for phone number validation
        if (normalizeInput(form.current["phone-number"].value) !== "" && !matchRegex(/^((\+\d{2,3}\s?\d)|(0\d))(\s?\d{2}){4}$/, normalizeInput(form.current["phone-number"].value))) {
            console.log("error: invalid phone number");
            setFormInputsValidity({...formInputsValidity, "phone": false});
            formValid = false;
        }

        //TODO password strength

        //Check for email and password confirmation
        if (email !== emailConfirmation){
            console.log("error: email don't match");
            formValid = false;
            const emailError = document.getElementsByClassName("email-error");
            emailError.innerText = "The email addresses do not match. Please check and try again.";
        }
        if (password !== passwordConfirmation){
            console.log("error: password don't match");
            formValid = false;
            const passwordError = document.getElementsByClassName("password-error");
            passwordError.innerText = "The passwords do not match. Please check and try again.";
        }

        //Check for user agreements
        if (!form.current["terms-of-services-checkbox-input"].checked) {
            console.log("error: terms of services not agreed");
            formValid = false;
        }
        return formValid;
    }

    return(
        <form className="content-section create-account-container" onSubmit={(e) => sendForm(e)} ref={form}>
            <h1 className="create-account">Créer un compte</h1>
            <h4 className="title-section">Your details</h4>

            <div className="container-personnel-data">
                <div className="basic-personnel-data">
                    <select name="subscription" id="subscription" className="data-selector" autoComplete="honorific-prefix">
                        <option value="subscription">Abonnement</option>
                        <option value="classique">Classique</option>
                        <option value="prenium">Prenium</option>
                    </select>
                    <div className="name-container">
                        {name.map((name) => (
                            <div key={name.id} className="name-container-input">
                                <label htmlFor={name.id}>{name.title}</label>
                                <br/>
                                <input name={name.id} id={name.id} type="text" className={((!formInputsValidity[name.id]) ? "invalid " : "") + "data-selector name-input"} maxLength="20" placeholder={"ex: " + name.example} aria-required={true}/>
                            </div>
                        ))}
                    </div>
                    <div className="email-container">
                        {email.map((email) => (
                            <div key={email.id} className="email-container-input">
                                <label htmlFor={email.id}>{email.title}</label>
                                <br/>
                                <input type={email.type} id={email.id} className={((!formInputsValidity[email.id]) ? "invalid " : "") + "data-selector email-input"} maxLength="35" placeholder={"ex: " + email.example} name={email.id} autoComplete="username" aria-required={true}/>
                            </div>
                        ))}
                        <div className="email-error"></div>
                    </div>
                    <div className="phone-container">
                        <div key={email.id} className="email-container-input">
                            <label htmlFor="phone-number">numéro de téléphone</label>
                            <br/>
                            <input type="tel" id="phone-number" className="data-selector email-input" maxLength="17" placeholder="ex: +33 6 34 17 39 43" name="phone-number" aria-required={true}/>
                        </div>
                    </div>
                    <div className="company-name">
                        <div key={email.id} className="company-container-input">
                            <label htmlFor="company-name">Nom de votre entreprise</label>
                            <br/>
                            <input type="text" id="company-name" name="company-name" aria-required={true}/>
                        </div>
                    </div>
                </div>
                <div className="password-data-container">
                    {password.map((password) => (
                        <div className="password-container-input">
                            <label htmlFor={password.id}>{password.title}</label>
                            <br/>
                            <input type="password" id={password.id} className={((!formInputsValidity[password.id]) ? "invalid " : "") + "data-selector password-input"} name={password.id} autoComplete="new-password" aria-required={true}/>
                        </div>
                    ))}
                    <div className="password-error"></div>
                </div>
            </div>
            <div className="checkbox-container">
                <label aria-required={true}><input type="checkbox" id="terms-of-services-checkbox-input" name="terms-of-services-checkbox-input" className="checkbox-input"/>J'accepte la <Link to={"../security-policy"}>politique de sécurité</Link> de RPS®</label>
            </div>
            <hr/>
            <button className="button create-account">Créer un compte</button>
            <button className="button create-account-login-button" onClick={() => navigate("../LogIn")}>Se connecter</button>
        </form>
    )
}

function LogIn({originPath, user, setUser, setCookie}){
    const navigate = useNavigate();
    const [submitActivated, setSubmitActivated] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const form = useRef(null);
    const errorMessage = useRef(null);

    function activateSubmit() {
        if (form.current["email"].value === "" || form.current["password"].value === "") {
            setSubmitActivated(false);
        } else if(!submitting) {
            setSubmitActivated(true);
        }
    }

    function sendForm(e) {
        e.preventDefault();
        if (checkData()) {
            setSubmitting(true);
            setSubmitActivated(false);
            axios({
                method: 'post',
                url: '/api/client/login',
                timeout: 4000, // 4 seconds timeout
                data: {
                    email: normalizeInput(form.current["email"].value),
                    password: form.current["password"].value
                }
            })
                .then(response => {
                    if (response.status === 200 || response.status === 304) {
                        setUser({clientID: response.data.clientID,
                            connectionToken: response.data.connectionToken});
                        setCookie("user", response.data, 2);
                        if (originPath.pathname !== "/account/login") {
                            navigate("/dashboard", {replace: true});
                        }
                        else {
                            navigate("./", {replace: true});
                        }
                    }
                })
                .catch(error => {
                    setSubmitting(false);
                    if (error.status === 404) {
                        errorMessage.current.innerText = error.response.data;
                    }
                    else if (error.status === 401 && error.statusText === "Unauthorized") {
                        errorMessage.current.innerText = error.response.data;
                    }
                    else {
                        console.error('error: ', error);
                    }
                    setSubmitActivated(true);
                });
        }
    }

    function checkData() {
        if (!matchRegex(/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, normalizeInput(form.current["email"].value))) {
            console.log("error: invalid email");
            errorMessage.current.innerText = "Invalid email";
            form.current["email"].focus();
            return false;
        } else if (form.current["password"].value === "") {
            return false;
        }
        errorMessage.current.innerText ="";
        return true;
    }



    return(
        <form className="content-section log-in" onSubmit={(e) => sendForm(e)} ref={form}>
            <h1 className="log-in-account">Se connecter</h1>
            <div className="log-in-container">
                <div className="log-in-item">
                    <label htmlFor="email">Email</label>
                    <br/>
                    <input type="email" id="email" placeholder="Enter your email..." className="data-selector log-in-selector" onChange={() => activateSubmit()} autoComplete="username"/>
                </div>
                <div className="log-in-item">
                    <label htmlFor="password">Password</label>
                    <br/>
                    <input type="password" id="password" placeholder="Enter your password..." className="data-selector log-in-selector" onChange={() => activateSubmit()} autoComplete="current-password"/>
                </div>
            </div>
            <p className="error-message" ref={errorMessage}></p>
            <div className="log-in-button-container">
                <Link to="/account/signin">I forgot my password</Link>
                <br/>
                <button type="submit" className="button log-in-button" disabled={!submitActivated}>Se connecter</button>
            </div>
            <button className="button create-account-login-button" onClick={() => navigate("../SingIn")}>Créer un compte</button>
        </form>
    )
}

function SignIn(){
    return(
        <AccountInformation name={nameData} email={emailData}/>
    )
}

export {SignIn, LogIn};