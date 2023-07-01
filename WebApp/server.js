const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require("fs");
const bcrypt = require("bcrypt");
const crypto = require("crypto");
const Client = require('ssh2').Client;
let mysql = require('mysql');
let multer = require('multer');

let moment = require('moment');
require('dotenv').config({path: ".env"});
const db_config = require('./db_config');

const MAX_BACKUPS = 3;

const app = express();
let connection = mysql.createConnection(db_config);

connection.connect((err) => {
    console.log('Connection done');
});

connection.on('error', function onError(err) {
    console.log('db error', err);
    throw err;
});

function refreshConnection() {
    if(connection.state !== "authenticated") {
        console.log("Refreshing connection");
        connection = mysql.createConnection(db_config);
        connection.connect((err) => {
            console.log('Connection done');
        });
    }
}

function getMachineID(req, res, next) {
    if (req.query.machineAddress) {
        let sql = "SELECT `machineID` FROM `Machine` WHERE `machineAddress`= ?";
        connection.query(sql, [req.query.machineAddress], (err, results, fields) => {
            if (!err) {
                if (results.length === 0) {
                    res.status(400).send("Cette machine n'est pas enregistrée");
                    return;
                }
                req.machineID = results[0].machineID.toString();
                next();
            }
            else {
                res.status(400).send("Cette machine n'est pas enregistrée pour ce client");
            }
        });
    }
    else {
        next()
    }
}

function checkMachineToken(req, res, next) {
    let token = req.headers.authorization; // Récupérer le token depuis l'en-tête
    if (token && token.startsWith("Bearer ")) {
        // Extraire le token en supprimant le préfixe "Bearer "
        token = token.substring(7);
        refreshConnection();
        connection.query(
            "SELECT * FROM `Machine` WHERE token=? AND machineID=? AND clientID=?",
            [token, req.machineID, req.params.clientId],
            (err, results) => {
                if (err) {
                    console.error("Erreur lors de la vérification du token :", err);
                    return res.sendStatus(500);
                }

                if (results.length === 0) {
                    // Token invalide ou non trouvé dans la base de données
                    return res.sendStatus(401); // Unauthorized
                }

                // Token valide, passer à l'étape suivante
                next();
            }
        );
    }
    else {
        return res.sendStatus(401);
    }
}

// Token associé à chaque client
function checkSessionToken(req, res, next) {
    let token = req.headers.authorization; // Récupérer le token depuis l'en-tête
    if (token && token.startsWith("Bearer ")) {
        // Extraire le token en supprimant le préfixe "Bearer "
        token = token.substring(7);
        refreshConnection();
        connection.query(
            "SELECT * FROM `Session` WHERE sessionToken=? AND clientID=?",
            [token, req.params.clientId],
            (err, results) => {
                if (err) {
                    if (err.code === "ERR_SOCKET_CONNECTION_TIMEOUT") {
                        console.error("Erreur lors de la vérification du token : connection timeout");
                        return res.status(500).send("Token checking timed-out");
                    }
                    console.error("Erreur lors de la vérification du token :", err);
                    return res.sendStatus(500);
                }

                if (results.length === 0) {
                    // Token invalide ou non trouvé dans la base de données
                    return res.sendStatus(401); // Unauthorized
                }

                // Token valide, passer à l'étape suivante
                next();
            }
        );
    }
    else {
        return res.sendStatus(401);
    }
}

function checkDestinationFolder(req, res, next){
    // Vérifier si le dossier de destination existe
    let destination = path.join(process.env.CLIENT_DATA_PATH, req.params.clientId);

    if (!fs.existsSync(destination)) {
        return res.status(400).send("Il semble que vous n'êtes pas client chez nous");
    }
    else {
        if (req.machineID) {
            if (!fs.existsSync(path.join(destination, req.machineID))) {
                fs.mkdirSync(path.join(destination, req.machineID));
            }
        }
        else {
            return;
        }
    }
    // Le dossier de destination existe, continuer le traitement des fichiers
    next();
}

function sendFile(req, res){
    let options = {
        headers: {
            'Content-Type': 'application/zip',
            'Content-Disposition': 'attachment'
        }
    }

    res.download(req.backupFileTempPath, options, (err) => {
        if (err) {
            console.log('Erreur lors du téléchargement du fichier', err);
            res.status(500).send('Erreur lors du téléchargement du fichier');
        } else {
            console.log('Fichier téléchargé avec succès');
            // Supprimer le fichier temporaire après le téléchargement
            fs.unlinkSync(req.backupFileTempPath);
        }
    });
}

// Configuration de Multer pour gérer les fichiers reçus
const upload = multer({ storage:
    multer.diskStorage({
        destination: function (req, file, cb) {
            // Spécifiez le dossier de destination pour les fichiers reçus
            cb(null, process.env.TEMP_PATH);
        },
        filename: function (req, file, cb) {
            // Générez un nom de fichier unique
            cb(null, file.originalname);
        }
    })
});

// Middleware de chiffrement du fichier
const encryptFile = (req, res, next) => {
    const files = req.files;

    // Clé de chiffrement
    const key = process.env.ENCRYPT_KEY;
    const algorithm = 'aes-256-ecb';
    const keyBytes = Buffer.from(key, 'hex');

    // Lire le contenu du fichier
    fs.readFile(files[0].path, (err, data) => {
        if (err) {
            console.error(err);
            return res.status(500).send('Erreur lors de la lecture du fichier.');
        }

        // Chiffrer le contenu du fichier
        const cipher = crypto.createCipheriv(algorithm, keyBytes, null);
        const encryptedData = Buffer.concat([cipher.update(data), cipher.final()]);

        // Chemin de destination pour enregistrer le fichier chiffré
        const destinationPath = path.join(process.env.CLIENT_DATA_PATH, req.params.clientId, req.machineID, files[0].originalname);

        // Enregistrer le fichier chiffré dans ClientData (process.env.CLIENT_DATA_PATH)
        fs.writeFile(destinationPath, encryptedData, (err) => {
            if (err) {
                console.error(err);
                return res.status(500).send("Erreur lors de l'enregistrement du fichier chiffré.");
            }
            // Supprimer le fichier d'origine qui se trouve dans le dossier temp
            fs.unlink(files[0].path, (err) => {
                if (err) {
                    console.error(err);
                }

                // Ajouter les informations du fichier chiffré à la requête
                req.encryptedFilePath = destinationPath;

                next();
            });
        });
    });
};

// Middleware de déchiffrement de fichier
const decryptFile = (req, res, next) => {
    // Vérifier si le dossier de destination existe
    let backupPath = path.join(process.env.CLIENT_DATA_PATH, req.params.clientId, req.machineID.toString(), req.backupFileName);
    if (!fs.existsSync(backupPath)) {
        return res.status(404).send("Il semble que ce backup n'existe pas.");
    }

    // Clé de déchiffrement
    const key = process.env.ENCRYPT_KEY;
    const algorithm = 'aes-256-ecb';
    const keyBytes = Buffer.from(key, 'hex');

    // Lire le contenu du fichier chiffré
    fs.readFile(backupPath, (err, encryptedData) => {
        if (err) {
            console.error(err);
            return res.status(500).send("Erreur lors de la lecture du fichier chiffré.");
        }

        // Déchiffrer le contenu du fichier
        const decipher = crypto.createDecipheriv(algorithm, keyBytes, null);
        const decryptedData = Buffer.concat([decipher.update(encryptedData), decipher.final()]);

        // Chemin de destination pour enregistrer le fichier déchiffré
        const backupTemppath = path.join(process.env.TEMP_PATH, req.backupFileName);

        // Enregistrer le fichier déchiffré à la destination spécifiée
        fs.writeFile(backupTemppath, decryptedData, (err) => {
            if (err) {
                console.error(err);
                return res.status(500).send("Erreur lors de l'enregistrement du fichier déchiffré.");
            }
            req.backupFileTempPath = backupTemppath;
            next();
        });
    });
}

function clearOldBackup(req, res, next) {
    let storage_folder = path.join(process.env.CLIENT_DATA_PATH, req.params.clientId, req.machineID);
    // Vérifier le nombre de sauvegardes existantes
    fs.readdir(storage_folder, (err, files) => {
        if (err) {
            console.error('Erreur lors de la lecture du dossier de sauvegardes :', err);
            return res.status(500).json({ message: 'Erreur lors de la gestion des sauvegardes.' });
        }

        // Vérifier si le nombre de sauvegardes atteint le maximum
        if (files.length > MAX_BACKUPS) {
            // Trier les fichiers par date de modification (plus ancien au plus récent)
            const sortedFiles = files.sort((a, b) => {
                return a.localeCompare(b);
            });

            // Supprimer la plus ancienne sauvegarde
            const oldestBackup = sortedFiles[0];
            const pathToOldestBackup = path.join(storage_folder, oldestBackup);
            fs.unlink(pathToOldestBackup, (err) => {
                if (err) {
                    console.error('Erreur lors de la suppression de la plus ancienne sauvegarde :', err);
                } else {
                    const sql="DELETE FROM `Backup` WHERE `machineID`=? AND `fileName`=?";

                    refreshConnection();
                    connection.query(sql, [req.machineID, oldestBackup], (err, results, fields) => {
                        if (!err) {
                            res.statusCode = 200;
                        }
                    });
                }
            });
        }

        // Passer à l'étape suivante (enregistrement de la nouvelle sauvegarde)
        next();
    });
}

function createSessionToken(req, res) {
    const sql="INSERT INTO `Session`(`clientID`, `sessionToken`, `grantDate`) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE `sessionToken`=?, `grantDate`=?;";

    const date = new Date();
    const connection_token = generateSecureKey(40);
    refreshConnection();
    connection.query(sql, [req.clientID, connection_token, date.toISOString(), connection_token, date.toISOString()], (err, results, fields) => {
        if (!err) {
            res.statusCode = 200;
            res.send({"clientID": req.clientID, "connectionToken": connection_token});
            console.log("[Client " + req.clientID + "] Login successful");
        }
        else {
            res.sendStatus(409);
            return console.error('error during query: ' + err.code);
        }
    });
}

function formatString(string) {
    return string.trim();
}

function generateSecureKey(length) {
    // Générer des octets aléatoires sécurisés
    const buffer = crypto.randomBytes(length);

    // Convertir les octets en une chaîne encodée en base64
    let base64String = buffer.toString('base64');

    // Supprimer les caractères spéciaux et les signes de ponctuation de la clé
    base64String = base64String
        .replace(/\+/g, '')
        .replace(/\//g, '')
        .replace(/=/g, '');

    // Tronquer la clé pour obtenir exactement 40 caractères
    return base64String.substring(0, length);
}

//parses request body and populates request.body
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

// Where to serve static content
app.use(express.static(path.join(__dirname, "site/build")));

app.post('/api/client/:clientId/backup/push', getMachineID, checkMachineToken, checkDestinationFolder, upload.array('files'), encryptFile, clearOldBackup, (req, res) => {
    //backup des données dans la database

    const sql="INSERT INTO `Backup` (`machineID`, `fileName`, `backupDate`, `backupSize`) " +
        "VALUES ((SELECT machineID FROM `Machine` WHERE `machineAddress`= ?), ?, ?, ?)";

    if (!req.files || req.files.length === 0) {
        return res.status(400).send("Aucun fichier n'a été reçu.");
    }

    // Réponse
    let clientID = req.params.clientId;
    let machineAddress = req.query.machineAddress;
    let backupDate = req.query.date;
    let files = req.files;

    // Vérifiez si le fichier est un fichier compressé (par exemple, ZIP)
    for (const file of files) {
        if (file.mimetype !== 'application/zip') {
            fs.unlinkSync(file.path);
            return res.status(400).send('Les dossiers doivent être compressés (ZIP)');
        }
    }

    refreshConnection();
    connection.query(sql, [machineAddress, files[0].filename, backupDate, files[0].size], (err, results, fields) => {
        if (!err) {
            res.status(201).send("Backup stored successfully");
            return console.log('['+ clientID + ' - ' + machineAddress + ']' + " Backup effectué avec succès !");
        }
        else {
            fs.unlinkSync(files[0].path);
            if (err.code === "ER_NO_REFERENCED_ROW_2") {
                res.status(404).send("Cette machine n'est pas enregistrée pour ce client");
            }
            else {
                res.status(400).send('error during query: ' + err.message);
                return console.error('error during query: ' + err.message);
            }
        }
    });
});

app.get('/api/client/:clientId/backup/:backupId/download', checkSessionToken, (req, res, next) => {
    //download d'un backup

    const sql="SELECT `machineID`, `fileName` FROM `Backup` WHERE `backupID`=?";

    let clientID = req.params.clientId;
    let backupID = req.params.backupId;

    refreshConnection();
    connection.query(sql, [backupID], (err, results, fields) => {
        if (!err) {
            req.machineID = results[0].machineID;
            req.backupFileName = results[0].fileName;
            next();
        }
        else {
            if (err.code === "ER_NO_REFERENCED_ROW_2") {
                res.status(404).send("Ce backup n'existe pas");
            }
            else {
                res.status(400).send('error during query: ' + err.message);
                return console.error('error during query: ' + err.message);
            }
        }
    });
}, decryptFile, sendFile);

app.post('/api/client/:clientId/machine/register', checkSessionToken,  (req, res) => {
    //add a new machine to a client account

    const sql="INSERT INTO `Machine`(`clientID`, `machineAddress`, `name`, `state`, `token`) " +
        "VALUES (?, ?, ?, ?, ?)";

    refreshConnection();
    connection.query(sql, [req.params.clientId, req.query.machineAddress, req.body.name, req.body.state, generateSecureKey(40)],(err, results, fields) => {
        if (!err) {
            res.statusCode = 201;
            res.send(results);
            console.log('Machine added');
        }
        else {
            res.sendStatus(409);
            return console.error('error during query: ' + err.code);
        }
    });
});

app.get('/api/client/:clientId/machine', checkSessionToken,  (req, res) => {
    //get machines
    //if the `machineId` param is specified, returns only the specified machine

    let sql = "SELECT * FROM `Machine` WHERE `clientID`=? ORDER BY `name`";
    let params = [req.params.clientId];

    if (req.query.machineId) {
        sql = "SELECT * FROM `Machine` WHERE `machineID`=? ORDER BY `name`";
        params = [req.query.machineId];
    }

    refreshConnection();
    connection.query(sql, params,(err, results, fields) => {
        if (!err) {
            res.statusCode = 200;
            res.send(results);
        }
        else {
            res.sendStatus(404);
            return console.error('error during query: ' + err.code);
        }
    });
});

app.get('/api/client/:clientId/machine/:machineId/backup', checkSessionToken,  (req, res) => {
    //get machine backups
    //if the `backupId` param is specified, returns only the specified backup

    let sql = "SELECT * FROM `Backup` WHERE `machineID`=? ORDER BY `backupDate` DESC";
    let params = [req.params.machineId];

    if (req.query.backupId) {
        sql = "SELECT * FROM `Backup` WHERE `machineID`=? AND `backupID`=?";
        params = [req.params.machineId, req.query.backupId];
    }

    refreshConnection();
    connection.query(sql, params,(err, results, fields) => {
        if (!err) {
            res.statusCode = 200;
            res.send(results);
        }
        else {
            res.sendStatus(404);
            return console.error('error during query: ' + err.code);
        }
    });
});

app.patch('/api/client/:clientId/machine/update', checkSessionToken,  (req, res) => {
    //add a new machine to a client account

    const sql="UPDATE `Machine` SET `machineAddress`=?, `name`=? WHERE `clientID`=? AND `machineID`=?";

    refreshConnection();
    connection.query(sql, [formatString(req.body.machineAddress), formatString(req.body.name), req.params.clientId, req.query.machineId],(err, results, fields) => {
        if (!err) {
            if (results.affectedRows !== 0) {
                console.log('Machine updated');
                res.statusCode = 201;
                res.send(results);
            }
            else {
                res.statusCode = 404;
                console.log('No machine updated');
            }
        }
        else {
            res.sendStatus(404);
            return console.error('error during query: ' + err.code);
        }
    });
});

app.delete('/api/client/:clientId/machine/delete', checkSessionToken,  (req, res) => {
    //delete a machine from a client account

    const sql="DELETE FROM `Machine` WHERE `clientID`=? AND `machineID`=?";

    refreshConnection();
    connection.query(sql, [req.params.clientId, req.query.machineId],(err, results, fields) => {
        if (!err) {
            if (results.affectedRows !== 0) {
                res.sendStatus(200);
                console.log('Machine deleted');
            }
            else {
                res.statusCode = 404;
                console.log('No machine deleted');
            }
        }
        else {
            res.sendStatus(409);
            return console.error('error during query: ' + err.code);
        }
    });
});

app.post('/api/client/:clientId/machine/error', getMachineID, checkMachineToken,  (req, res) => {
    //add a new error

    const sql="INSERT INTO `Error`(`machineID`, `type`, `file_path`, `date`, `message`) VALUES (?, ?, ?, ?, ?)";

    refreshConnection();
    connection.query(sql, [req.machineID, req.body.type, req.body.path, req.body.date, req.body.message],(err, results, fields) => {
        if (!err) {
            res.statusCode = 201;
            res.send(results);
            console.log('Error added');
        }
        else {
            res.sendStatus(409);
            return console.error('error during query: ' + err.code);
        }
    });
});

app.get('/api/client/:clientId/machine/error', checkSessionToken,  (req, res) => {
    //get errors
    //if the `machineId` param is specified, returns only the errors of this machine

    let sql = "SELECT * FROM `Error` JOIN `Machine` USING(machineID) WHERE `clientID`=? ORDER BY `Error`.`date` DESC";
    let params = [req.params.clientId];

    if (req.query.machineId) {
        sql="SELECT * FROM `Error` WHERE `machineID`=?";
        params = [req.query.machineId];
    }

    refreshConnection();
    connection.query(sql, params,(err, results, fields) => {
        if (!err) {
            res.statusCode = 200;
            res.send(results);
        }
        else {
            res.sendStatus(404);
            return console.error('error during query: ' + err.code);
        }
    });
});

// Creation de client
app.post('/api/client/register', (req, res) => {
    //add a client account
    /*
    Body json:
    {
    "email": "",
    "password":"",
    "firstName":"",
    "lastName":"",
    "phone":0,
    "company":"",
    "subscription":""
    }
    */

    let client = req.body;
    let cypheredPassword = "";

    const sql="INSERT INTO `Client`(`clientID`, `email`, `password`, `firstName`, `lastName`, `phone`, `company`, `subscription`) " +
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
    let clientID = generateSecureKey(10);
    refreshConnection();
    bcrypt.hash(client.password, 10, function(err, hash) {
        if (!err) {
            cypheredPassword = hash;
        }
        else {
            cypheredPassword = client.password;
        }
        // Create a folder named clientID in ClientData directory
        const folderPath = 'ClientData/' + clientID;
        fs.mkdir(folderPath, (err) => {
            if (err) {
                console.error('Failed to create client folder:', err);
            }
            else {
                connection.query(sql, [clientID, formatString(client.email), cypheredPassword, formatString(client.firstName), formatString(client.lastName), client.phone, formatString(client.company), client.subscription],(err, results, fields) => {
                    if (!err) {
                        res.statusCode = 201;
                        res.send(results);
                        console.log('Client successfully created');
                    }
                    else {
                        console.log(err);
                        res.statusCode = 409;
                        res.send(err.code);
                        // Delete the ClientID file in ClientData/
                        fs.rmdir(folderPath, (err) => {
                            if (err) {
                                console.error('Failed to remove client folder:', err);
                            } else {
                                console.log('Client folder removed:', folderPath);
                            }
                        });
                        return console.error('error during query: ' + err.code);
                    }
                });
            }
        });
    });
});

app.post('/api/client/login', (req, res, next) => {
    //check if credentials match client data
    /*
    Body json:
    {
    "email": "",
    "password":""
    }
    */

    let creds = req.body;
    const sql="SELECT `password`, `clientID` FROM `Client` WHERE `email`= ?";

    refreshConnection();
    connection.query(sql, [formatString(creds.email)],(err, results, fields) => {
        if (!err && results.length !== 0) {
            bcrypt.compare(creds.password, results[0].password, function(err, result) {
                if (result) {
                    req.clientID = results[0].clientID;
                    next()
                }
                else {
                    res.statusCode = 401;
                    res.send("Password invalid");
                }
            });
        }
        else {
            res.statusCode = 404;
            res.send("This account doesn't exist");
        }
    });
}, createSessionToken);

app.get('/api/client/:clientId', checkSessionToken, (req, res) => {
    //get account data

    const sql="SELECT `clientID`, `email`, `firstName`, `lastName`, `phone`, `company`, `subscription` FROM `Client` WHERE `clientID`=?";

    refreshConnection();
    connection.query(sql, [req.params.clientId],(err, results, fields) => {
        if (!err) {
            if (results.length !== 0) {
                res.status(200).send(results[0]);
            }
            else {
                res.statusCode = 404;
                res.send("This account doesn't exist");
            }
        }
        else {
            res.statusCode = 404;
            res.send("This account doesn't exist");
            return console.error('error during query: ' + err.message);
        }
    });
});

app.get('/api/*', (req, res) => {
    res.send("Ransomware Protection System (RPS) API endpoint\nStatus: " + connection.state);
});

app.get('/*', (req, res) => {
    try {
        res.sendFile(path.join(__dirname, "site/build/index.html"));
    }
    catch (error) {
        console.log(error);
    }
});

app.listen(process.env.PORT || process.env.SERVER_PORT, () => {
    console.log("===============================================");
    console.log("Application is started and listening on port " + process.env.SERVER_PORT);
    console.log("Access the server on: http://localhost:" + process.env.SERVER_PORT);
});
