import React from 'react';
import NavBar from '../components/NavBar';
import './HomePage.css';

export default function HomePage() {
    return (
        <div>
            <NavBar />

            <div id="app">
                <section id="about-us">
                    <h2>Qui sommes-nous ?</h2>
                    <img src="https://upload.wikimedia.org/wikipedia/commons/3/38/Info_Simple.svg" alt="À propos de nous" />
                    {/* <p>Source : Wikipédia</p> */}
                    <p>
                        Nous sommes une <strong>équipe d'étudiants en troisième année à l'EFREI Paris</strong>, passionnés par
                        la <i>cybersécurité</i>. Au sein de <strong>HackFactorizz</strong>, nous nous consacrons à la <strong>protection
                            des petites entreprises</strong> contre les menaces croissantes des ransomwares, en concevant
                        des solutions <i>simples</i> et <i>abordables</i>.
                    </p>
                </section>

                <section id="context">
                    <h2>Le contexte</h2>
                    <img src="https://www.commvault.com/wp-content/uploads/2020/12/ransomware-protection.svg" alt="Contexte" />
                    {/* <p>Source : Commvault</p> */}
                    <p>
                        Les <strong>ransomwares</strong> sont des <em>logiciels malveillants</em> qui cryptent les données des entreprises,
                        puis exigent une rançon pour leur déchiffrement. Cette forme de <strong>cyberattaque</strong> peut avoir des conséquences
                        dévastatrices, en particulier pour les <strong>petites entreprises</strong> comme les cabinets médicaux ou les bureaux
                        d'avocats. Pour contrer cette menace, une <em>solution de protection efficace, facile à utiliser et
                            à mettre en place</em> est essentielle.
                    </p>
                </section>

                <section id="objective">
                    <h2>L'objectif</h2>
                    <img src="https://cdn1.iconfinder.com/data/icons/business-sets/512/target-512.png" alt="Objectif" />
                    {/* <p>Source : Adobe iConfinder</p> */}
                    <p>
                        Notre objectif est de développer une <strong>solution automatique</strong> pour se prémunir contre les <strong>ransomwares</strong>. Cette solution comprend la conception et la mise en œuvre d'un <em>dispositif anti-ransomware</em> qui se caractérise par sa <strong>simplicité d'utilisation</strong> et son <strong>efficacité</strong> dans la lutte contre ces logiciels malveillants.
                    </p>
                </section>

                <section id="rps-solution">
                    <h2>La Solution RPS</h2>
                    <img src="https://assets.entrepreneur.com/content/3x2/2000/20190612193425-GettyImages-1066987316-crop.jpeg" alt="Solution" />
                    {/* <p>Source : Entrepreneur</p> */}
                    <p>
                        Les <strong>petites entreprises</strong>, tels que les cabinets médicaux ou les bureaux d'avocats, sont souvent les plus vulnérables face aux <em>cyberattaques</em> et en particulier 
                        aux <strong>ransomwares</strong>. Les conséquences de ces attaques peuvent être dévastatrices, de la perte de données à
                        des perturbations opérationnelles majeures. Malheureusement, ces entreprises manquent souvent des ressources pour mettre
                        en place une sécurité sophistiquée.
                    </p>
                    <p>
                        Pour répondre à ce besoin crucial, notre entreprise, <strong>HackFactorizz</strong>, a développé <em>RPS (Ransomware Protection Software)</em>. Cette
                        application fournit une protection efficace contre les ransomwares et est <strong>simple à installer et à utiliser</strong>. Spécifiquement
                        destinée aux petites entreprises, RPS offre une protection fiable et abordable, rendant la <em>cybersécurité accessible à tous</em>.
                        Avec RPS, la protection contre les ransomwares est désormais à portée de main pour toutes les entreprises.
                    </p>
                </section>

                <section id="features">
                    <h2>Caractéristiques de RPS</h2>
                    <div className="features-list">
                        <div className="feature-item">
                            <h3><strong>Détection et prévention précoce des ransomwares</strong></h3>
                            <p>RPS est capable de <em>détecter les ransomwares avant leur infiltration</em> dans votre système, vous permettant ainsi de prendre des mesures préventives en temps opportun.</p>
                        </div>
                        <div className="feature-item">
                            <h3><strong>Sauvegarde automatique des données vitales</strong></h3>
                            <p>RPS crée <em>automatiquement des sauvegardes</em> de vos données les plus importantes, permettant leur restauration en cas d'attaque de ransomware.</p>
                        </div>
                        <div className="feature-item">
                            <h3><strong>Interface utilisateur conviviale</strong></h3>
                            <p>Doté d'une interface utilisateur conçue pour être <em>facile et intuitive</em>, RPS est utilisable même pour ceux qui n'ont pas d'expérience en informatique.</p>
                        </div>
                        <div className="feature-item">
                            <h3><strong>Alertes en temps réel sur les menaces émergentes</strong></h3>
                            <p>RPS vous alerte <em>en temps réel</em> en cas de détection d'une menace, vous permettant de réagir rapidement pour protéger vos données.</p>
                        </div>
                    </div>
                </section>

                <section id="pricing">
                    <h2>Tarification RPS</h2>
                    <img src="https://images.pexels.com/photos/590022/pexels-photo-590022.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940" alt="Pricing" />
                    {/* <p>Source : Pexels</p> */}
                    <p>
                        Nous proposons une formule d'abonnement <strong>simple et abordable</strong>. Pour seulement 10€ par mois, vous bénéficiez d'une
                        protection complète contre les ransomwares, comprenant des fonctionnalités de <em>détection précoce et de sauvegarde
                            automatique des données</em>.
                    </p>
                    <p>
                        Votre abonnement inclut également un <strong>support client 24/7</strong>. Vous pouvez nous contacter à tout moment si vous avez des questions ou des préoccupations. Notre priorité est de vous aider à protéger votre entreprise.
                    </p>
                    <p>
                        Pour toute information supplémentaire sur notre tarification ou pour discuter de besoins spécifiques, n'hésitez pas à <em>nous contacter</em>.
                    </p>
                </section>

                <section id="advantages">
                    <h2>Les bénéfices de RPS</h2>
                    <img src="https://www.patrimandco.fr/sites/www.patrimandco.fr/files/wysiwyg/avantages.jpg" alt="Avantages" />
                    {/* <p>Source : Patrim&Co</p> */}
                    <p>
                        RPS est une solution complète offrant <strong>une protection robuste contre les ransomwares</strong>, le tout avec une simplicité d'utilisation particulièrement adaptée aux petites entreprises. Profitez de nos fonctionnalités uniques de détection précoce, de prévention des attaques et de sauvegarde automatique des données.
                    </p>
                    <div className="table-comparison">
                        <table>
                            <tbody>
                                <tr>
                                    <th>RPS</th>
                                    <th>Autres Applications</th>
                                </tr>
                                <tr>
                                    <td><strong>Simplicité d'utilisation</strong></td>
                                    <td>Complexité et besoins en formation</td>
                                </tr>
                                <tr>
                                    <td><strong>Protection efficace contre les ransomwares</strong></td>
                                    <td>Protection inégale et souvent insuffisante</td>
                                </tr>
                                <tr>
                                    <td><strong>Détection précoce et prévention des attaques</strong></td>
                                    <td>Prévention tardive ou absence de prévention</td>
                                </tr>
                                <tr>
                                    <td><strong>Abordable</strong></td>
                                    <td>Coûteux ou comportant des frais cachés</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </section>

                <section id="automation">
                    <h2>Automatisation avec RPS</h2>
                    <img src="https://static.vecteezy.com/ti/vecteur-libre/p1/14195103-icone-du-systeme-automatise-sur-fond-blanc-signe-d-automatisation-symbole-de-controle-electronique-style-plat-vectoriel.jpg" alt="Automatisation" />
                    {/* <p>Source : Vecteezy</p> */}
                    <p>
                        L'automatisation est au cœur de RPS. De la sauvegarde des données à la détection des menaces et à la prévention
                        des attaques, tout est conçu pour fonctionner <em>avec le minimum d'interventions humaines</em>. Cette automatisation
                        garantit une protection constante et permet aux entreprises de se concentrer sur leurs opérations essentielles.
                    </p>
                </section>

                <section id="download">
                    <h2>Sécurisez votre entreprise dès maintenant avec RPS !</h2>
                    <p>
                        Ne laissez pas votre entreprise devenir la prochaine victime d'une attaque de
                        ransomware. <strong>Téléchargez RPS aujourd'hui</strong> et protégez votre entreprise contre les menaces en ligne.
                    </p>
                </section>
            </div>
        </div>
    );
}
