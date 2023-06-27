import React from 'react';
import ReturnHome from '../components/ReturnHome';
import Contacts from '../assets/contact.json';
import './Contact.css';

export default function Contact() {
    const contacts = Contacts;
    return (
        <div>
            <ReturnHome />
            <div id="contact-us">
                <h2>Contactez-nous</h2>
                <p className="intro">
                    Nous sommes un groupe d'étudiants en cybersécurité à l'EFREI, passionnés par la protection des données et la prévention des attaques
                    informatiques. Nous avons développé RPS dans le cadre de nos études, et nous serions ravis de répondre à vos questions, de discuter
                    de nos recherches, ou d'explorer des collaborations potentielles.
                </p>
                <div className="grid-container">
                    {contacts.map((contact) => (
                        <div className="contact-item" key={contact.id}>
                            <h3>
                                {contact.firstName} {contact.lastName}
                            </h3>
                            <p>Email : {contact.email}</p>
                            <p>{contact.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
